pragma solidity ^0.8.0;

contract FoodChainTrace {

    struct Product {
        uint productId;
        string productName;
        address producer;
        string productionDate;
        string certification;
        address[] waypoints;
    }


    mapping(uint => Product) public products;
    uint public productCount;


    event ProductRegistered(uint indexed productId, string productName, address indexed producer);


    function registerProduct(string memory _productName, string memory _productionDate, string memory _certification) public {
        productCount++;
        products[productCount] = Product(productCount, _productName, msg.sender, _productionDate, _certification, new address[](0)); // Initialize with an empty array
        emit ProductRegistered(productCount, _productName, msg.sender);
    }

    function addWaypoint(uint _productId, address _waypoint) public {
        require(products[_productId].producer == msg.sender, "Only the producer can add waypoints");
        products[_productId].waypoints.push(_waypoint);
    }
}