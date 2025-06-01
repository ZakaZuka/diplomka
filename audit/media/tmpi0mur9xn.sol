// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";


contract FixedReentrancy {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public nonReentrant {
        uint amount = balances[msg.sender];
        require(amount > 0, "Insufficient balance");

        balances[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}