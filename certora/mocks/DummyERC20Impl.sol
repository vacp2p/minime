// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;

contract DummyERC20Impl {
    uint256 t;
    mapping (address => uint256) b;
    mapping (address => mapping (address => uint256)) a;

    string public name;
    string public symbol;
    uint public decimals;

    function balanceOfAt(address _owner, uint _blockNumber) public view returns (uint) {
        return b[_owner];
    }

    /**
     * @notice Total amount of tokens at a specific `_blockNumber`.
     * @param _blockNumber The block number when the totalSupply is queried
     * @return The total amount of tokens at `_blockNumber`
     */
    function totalSupplyAt(uint _blockNumber) public view returns(uint) {
        return t;
    }
}