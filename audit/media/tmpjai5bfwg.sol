// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title FoodChainTrace
 * @notice Пример смарт-контракта для отслеживания цепочки поставок продуктов питания
 *         с безопасной моделью pull-платежей (balances ➜ withdraw).
 */
contract FoodChainTrace is Ownable, ReentrancyGuard {
    /// @dev Этапы жизненного цикла продукта
    enum Stage {
        Produced,   // изготовлен
        Processed,  // переработан / очищен
        Packed,     // упакован
        Shipped,    // отгружен
        Delivered   // получен конечным получателем
    }

    /// @dev Информация о продукте
    struct Product {
        uint256 id;            // уникальный идентификатор
        string  name;          // наименование
        string  origin;        // происхождение (ферма, страна и т.п.)
        Stage   stage;         // текущий этап
        address currentHolder; // чей сейчас на балансе (производитель, перевозчик, магазин…)
        uint256 lastUpdated;   // timestamp последнего изменения
    }

    /** Счётчик идентификаторов продуктов */
    uint256 private _nextProductId = 1;

    /** productId ➜ Product */
    mapping(uint256 => Product) private _products;

    /** holder ➜ список productId, которыми он сейчас владеет */
    mapping(address => uint256[]) private _holderProducts;

    /**
     *  Модель pull-платежей: каждая сумма аккумулируется во внутреннем балансе,
     *  а адрес сам инициирует вывод (withdraw).
     */
    mapping(address => uint256) public balances;

    /* ──────────── Events ──────────── */
    event ProductRegistered(uint256 indexed id, string name, string origin, address indexed producer);
    event StageAdvanced(uint256 indexed id, Stage stage, address indexed actor);
    event Deposit(address indexed sender, address indexed beneficiary, uint256 amount);
    event Withdraw(address indexed receiver, uint256 amount);

    /* ──────────── Supply-chain логика ──────────── */

    /**
     * @notice Регистрация нового продукта. Этап по умолчанию — Produced.
     */
    function registerProduct(string calldata name, string calldata origin) external {
        uint256 id = _nextProductId++;
        _products[id] = Product({
            id: id,
            name: name,
            origin: origin,
            stage: Stage.Produced,
            currentHolder: msg.sender,
            lastUpdated: block.timestamp
        });

        _holderProducts[msg.sender].push(id);
        emit ProductRegistered(id, name, origin, msg.sender);
    }

    /**
     * @notice Перевод продукта к следующему этапу и новому держателю.
     *         Текущий держатель должен вызвать.
     * @param id        идентификатор продукта
     * @param newHolder адрес нового держателя (логист, магазин, клиент и т.д.)
     */
    function advanceStage(uint256 id, address newHolder) external {
        Product storage p = _products[id];
        require(p.currentHolder == msg.sender, "FoodChainTrace: not product holder");
        require(uint8(p.stage) < uint8(Stage.Delivered), "FoodChainTrace: already delivered");
        require(newHolder != address(0), "FoodChainTrace: new holder is zero");

        // Обновляем этап и держателя
        p.stage = Stage(uint8(p.stage) + 1);
        p.currentHolder = newHolder;
        p.lastUpdated = block.timestamp;
        _holderProducts[newHolder].push(id);

        emit StageAdvanced(id, p.stage, msg.sender);
    }

    /**
     * @notice Публичный view-метод для получения полной информации о продукте.
     */
    function getProduct(uint256 id) external view returns (Product memory) {
        return _products[id];
    }

    /**
     * @notice Id-шники продуктов, которыми в данный момент владеет `holder`.
     */
    function productsOf(address holder) external view returns (uint256[] memory) {
        return _holderProducts[holder];
    }

    /* ──────────── Pull-payments ──────────── */

    /**
     * @notice Депозит средств в пользу `beneficiary`. Платёж не переводится сразу,
     *         а добавляется во внутренний баланс, который получатель может вывести сам.
     */
    function deposit(address beneficiary) external payable {
        require(msg.value > 0, "FoodChainTrace: no ether sent");
        require(beneficiary != address(0), "FoodChainTrace: beneficiary is zero");
        balances[beneficiary] += msg.value;
        emit Deposit(msg.sender, beneficiary, msg.value);
    }

    /**
     * @notice Безопасное снятие средств со своего внутреннего баланса.
     *         Использует паттерн Checks-Effects-Interactions + ReentrancyGuard.
     */
    function withdraw() external nonReentrant {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "FoodChainTrace: nothing to withdraw");

        // Effects
        balances[msg.sender] = 0;

        // Interaction
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "FoodChainTrace: transfer failed");

        emit Withdraw(msg.sender, amount);
    }

    /**
     * @dev Fallback-функция: если кто-то случайно отправил ether контракту, зачисляем
     *      их на его внутренний баланс, чтобы не «повисли».
     */
    receive() external payable {
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.sender, msg.value);
    }
}