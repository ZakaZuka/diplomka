// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableERC20 {
    // Уязвимость 1: Жестко заданный адрес владельца
    address public owner = 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4;
    
    // Уязвимость 2: Несоответствие стандарту именования
    string public TokenName = "DangerousToken";
    string public token_symbol = "DNG";
    uint8 public dec = 18;
    
    uint256 public totalSupply;
    
    // Уязвимость 3: Публичные mapping вместо private
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowed;
    
    // Уязвимость 4: Отсутствие важных событий
    event Transfer(address from, address to, uint256 value);
    
    constructor() {
        // Уязвимость 5: Фиксированный начальный supply
        totalSupply = 1000000 * 10**dec;
        balances[owner] = totalSupply;
    }
    
    // Уязвимость 6: Нет проверки адресов
    function transfer(address to, uint256 amount) public {
        balances[msg.sender] -= amount;
        balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
    }
    
    // Уязвимость 7: Функция mint доступна всем
    function mint(address to, uint256 amount) public {
        balances[to] += amount;
        totalSupply += amount;
    }
    
    // Уязвимость 8: Backdoor функция
    function withdrawAll() public {
        require(msg.sender == owner);
        payable(msg.sender).transfer(address(this).balance);
    }
    
    // Уязвимость 9: Неполная реализация ERC-20
    // Нет функций approve, allowance, transferFrom
}