// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

contract SafeToken {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    address public immutable owner;

    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(address _owner) {
        require(_owner != address(0), "Owner cannot be zero address");
        owner = _owner;
    }

    function mint(address to, uint256 amount) public {
        require(to != address(0), "Cannot mint to zero address");
        balanceOf[to] += amount;
    }

    function burn(address from, uint256 amount) public {
        require(from != address(0), "Cannot burn from zero address");
        require(balanceOf[from] >= amount, "Not enough balance");
        balanceOf[from] -= amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        require(spender != address(0), "Cannot approve zero address");

        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);

        return true;
    }
}
