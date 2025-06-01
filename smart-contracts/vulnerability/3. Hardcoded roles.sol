// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HardcodedOwnerToken {
    // Основная уязвимость: жестко прописанный адрес владельца
    address public owner = 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4;
    
    // Нарушения стандарта ERC-20 для демонстрации
    string public name = "HardcodedToken";
    string public symbol = "HCT";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor() {
        // Уязвимость: фиксированный supply, привязанный к hardcoded owner
        totalSupply = 1_000_000 * (10 ** decimals);
        _balances[owner] = totalSupply;
        emit Transfer(address(0), owner, totalSupply);
    }

    // Уязвимость: отсутствие проверки адресов в transfer
    function transfer(address to, uint256 amount) public returns (bool) {
        _balances[msg.sender] -= amount;
        _balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    // Уязвимость: функция mint доступна только hardcoded owner
    function mint(address to, uint256 amount) public {
        require(msg.sender == owner, "Only hardcoded owner can mint");
        _balances[to] += amount;
        totalSupply += amount;
        emit Transfer(address(0), to, amount);
    }

    // Уязвимость: backdoor функция для hardcoded owner
    function emergencyWithdraw() public {
        require(msg.sender == owner, "Only hardcoded owner can withdraw");
        payable(owner).transfer(address(this).balance);
    }

    // Неполная реализация ERC-20 (умышленно)
    function approve(address spender, uint256 amount) public returns (bool) {
        _allowances[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }
}