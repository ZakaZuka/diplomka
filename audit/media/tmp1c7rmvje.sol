// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableToken1 {
    mapping(address => uint256) public balanceOf;

    function mint(address to, uint256 amount) public {
        // ❌ Нет проверки на address(0)
        balanceOf[to] += amount;
    }

    function burn(address from, uint256 amount) public {
        // ❌ Нет проверки на address(0)
        require(balanceOf[from] >= amount, "Not enough balance");
        balanceOf[from] -= amount;
    }

    mapping(address => mapping(address => uint256)) public allowance;

    function approve(address spender, uint256 amount) public {
        // ❌ Нет проверки на address(0)
        allowance[msg.sender][spender] = amount;
    }

    address public owner;

    constructor(address _owner) {
        // ❌ Нет проверки на address(0)
        owner = _owner;
    }
}