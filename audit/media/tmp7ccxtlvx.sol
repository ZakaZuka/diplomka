// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

contract FixedReentrancy {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "Nothing to withdraw");

        // Обнуляем баланс до отправки
        balances[msg.sender] = 0;

        // Отправляем средства, выбрасывает исключение при неудаче
        payable(msg.sender).Transfer(amount);
    }
}