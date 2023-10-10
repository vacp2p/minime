// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;

contract DummyERC20Impl {
    uint256 public t;
    mapping (address owner => uint256 balance) public balances;
    mapping (address holder => mapping (address spender => uint256 amount)) public allowances;

    string public name;
    string public symbol;
    uint256 public decimals;

    // solhint-disable-next-line no-unused-vars
    function balanceOfAt(address _owner, uint _blockNumber) public view returns (uint) {
        return balances[_owner];
    }

    /**
     * @notice Total amount of tokens at a specific `_blockNumber`.
     * @param _blockNumber The block number when the totalSupply is queried
     * @return The total amount of tokens at `_blockNumber`
     */
    // solhint-disable-next-line no-unused-vars
    function totalSupplyAt(uint _blockNumber) public view returns(uint) {
        return t;
    }
}
