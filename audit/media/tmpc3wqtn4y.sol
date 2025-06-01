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
}