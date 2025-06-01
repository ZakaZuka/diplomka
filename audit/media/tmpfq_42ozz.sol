// SPDX-License-Identifier: MIT
pragma solidity =0.8.30;

contract OverflowVulnerable {
    mapping(address => uint256) public balances;

    function withdraw(uint256 amount) public {
        balances[msg.sender] -= amount; // Возможен underflow (если amount > balance)
        payable(msg.sender).transfer(amount);
    }

    // Функция пополнения баланса для теста
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
}