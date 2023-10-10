// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;

contract DummyERC20ImplA {
    uint256 public t;
    mapping (address owner => uint256 amount) public balances;
    mapping (address holder => mapping (address spender => uint256 amount)) public allowances;

    string public name;
    string public symbol;
    uint256 public decimals;

    function myAddress() public returns (address) {
        return address(this);
    }

    function add(uint a, uint b) internal pure returns (uint256) {
        uint c = a + b;
        require (c >= a, "c is less than a");
        return c;
    }
    function sub(uint a, uint b) internal pure returns (uint256) {
        require (a >= b, "a is less than b");
        return a - b;
    }

    function totalSupply() external view returns (uint256) {
        return t;
    }
    function balanceOf(address account) external view returns (uint256) {
        return balances[account];
    }
    function transfer(address recipient, uint256 amount) external returns (bool) {
        balances[msg.sender] = sub(balances[msg.sender], amount);
        balances[recipient] = add(balances[recipient], amount);
        return true;
    }
    function allowance(address owner, address spender) external view returns (uint256) {
        return allowances[owner][spender];
    }
    function approve(address spender, uint256 amount) external returns (bool) {
        allowances[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool) {
        balances[sender] = sub(balances[sender], amount);
        balances[recipient] = add(balances[recipient], amount);
        allowances[sender][msg.sender] = sub(allowances[sender][msg.sender], amount);
        return true;
    }

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
