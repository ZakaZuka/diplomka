// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FixedReentrancy {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "Nothing to withdraw");

        //Обнуление баланса
        balances[msg.sender] = 0;

        //После чего отправляев эфир
        (bool success, ) = payable(msg.sender).transfer(amount);
        require(success, "Transfer failed");
    }
}