function withdraw() public {
    uint amount = balances[msg.sender];
    if (amount > 0) {
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;
    }
}