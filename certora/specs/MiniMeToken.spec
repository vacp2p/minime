using DummyERC20ImplA as DummyERC20;
using DummyController as DummyController;
using DummyERC20Impl as DummyERC20Impl;

methods {
    function _.transfer(address _to, uint256 _amount) external => DISPATCHER(true);
    function transferFrom(address _from, address _to, uint256 _amount) external returns (bool);
    function doTransfer(address _from, address _to, uint _amount) internal returns (bool);
    function doApprove(address _from, address _spender, uint256 _amount) internal  returns (bool);
    function _mint(address, uint) internal returns (bool);
    function _burn(address _owner, uint _amount) internal returns (bool);
    function _.balanceOf(address _owner) external => DISPATCHER(true);
    function approve(address _spender, uint256 _amount) external returns (bool);
    function allowance(address _owner, address _spender) external returns (uint256) envfree;
    function approveAndCall(address _spender, uint256 _amount, bytes memory _extraData) external returns (bool);
    function totalSupply() external returns (uint);
    function balanceOfAt(address _owner, uint _blockNumber) external returns (uint) envfree;
    function totalSupplyAt(uint _blockNumber) external returns (uint) envfree;
    function generateTokens(address _owner, uint _amount) external returns (bool); // onlyController
    function destroyTokens(address _owner, uint _amount) external returns (bool); // onlyController
    function enableTransfers(bool _transfersEnabled) external; // onlyController
    function isContract(address _addr) internal returns(bool);
    function min(uint a, uint b) internal returns (uint);
    function claimTokens(address _token) external; // onlyController
    function permit( address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) external;
    function nonces(address owner) external returns (uint256);
    function DOMAIN_SEPARATOR() external returns (bytes32);

    // Getters:
    function creationBlock() external returns (uint) envfree;
    function transfersEnabled() external returns (bool) envfree;
    function parentSnapShotBlock() external returns (uint) envfree;
    function controller() external returns (address) envfree;

    // Harness:
    function getCheckpointsLengthByAddress(address user) external returns (uint256) envfree;
    function getLatestBlockNumberByAddress(address user) external returns (uint256) envfree;
    function getCheckpointByAddressAndIndex(address user, uint256 index) external returns (MiniMeBase.Checkpoint) envfree;
    function getFromBlockByAddressAndIndex(address user, uint256 index) external returns (uint256) envfree;
     
    // Summarizations:
    function _.onTransfer(address _from, address _to, uint _amount) external => ALWAYS(true);
    function _.onApprove(address _from, address _spender, uint _amount) external => NONDET;
    function _.receiveApproval(address from, uint256 _amount, address _token, bytes _data) external => NONDET;
    function _.proxyPayment(address) external => NONDET;
    function DummyController.transfer(address, uint256) external returns (bool) => NONDET;

}

definition MaxHistoryRecords() returns uint256 = 1000000;

ghost mapping(address => mapping(uint256 => uint128)) fromBlocks {
    axiom forall address user . forall uint256 index1 . fromBlocks[user][index1] == 0;
}
ghost mapping(uint256 => uint128) totalSupplyFromBlocks {
    axiom forall uint256 index1 . totalSupplyFromBlocks[index1] == 0;
}
ghost mapping(address => mapping(uint256 => uint128)) values;
ghost mapping(uint256 => uint128) totalSupplyvalues;

// Mirror total supply history checkpoits values
hook Sload uint128 _value totalSupplyHistory[INDEX uint256 indx].value STORAGE {
    require totalSupplyvalues[indx] == _value;
}

hook Sstore totalSupplyHistory[INDEX uint256 indx].value uint128 _value (uint128 old_value) STORAGE {
    totalSupplyvalues[indx] = _value;
}

// Mirror total supply history checkpoits fromBlocks
hook Sload uint128 _fromBlock totalSupplyHistory[INDEX uint256 indx].fromBlock STORAGE {
    require totalSupplyFromBlocks[indx] == _fromBlock;
}

hook Sstore totalSupplyHistory[INDEX uint256 indx].fromBlock uint128 _fromBlock (uint128 old_fromBlock) STORAGE {
    totalSupplyFromBlocks[indx] = _fromBlock;
}

// Mirror balances history checkpoits values
hook Sload uint128 _value balances[KEY address user][INDEX uint256 indx].value STORAGE {
    require values[user][indx] == _value;
}

hook Sstore balances[KEY address user][INDEX uint256 indx].value uint128 _value (uint128 old_value) STORAGE {
    values[user][indx] = _value;
}

// Mirror balances history checkpoits fromBlocks
hook Sload uint128 _fromBlock balances[KEY address user][INDEX uint256 indx].fromBlock STORAGE {
    require fromBlocks[user][indx] == _fromBlock;
}

hook Sstore balances[KEY address user][INDEX uint256 indx].fromBlock uint128 _fromBlock (uint128 old_fromBlock) STORAGE {
    fromBlocks[user][indx] = _fromBlock;
}

// Limit history records to avoid overflows.
hook Sload uint256 _length balances[KEY address user].(offset 0) STORAGE {
    require _length < MaxHistoryRecords();
}

hook Sload uint256 _length totalSupplyHistory.(offset 0) STORAGE {
    require _length < MaxHistoryRecords();
}

// function that filtered out do not change the total supply
function doesntChangeBalance(method f) returns bool {
    return (f.selector != sig:generateTokens(address, uint).selector &&
        f.selector != sig:claimTokens(address).selector &&
        f.selector != sig:destroyTokens(address, uint).selector);
}

/*
    @Description:
        Each checkpoint.fromBlock must be less than the current blocknumber (no checkpoints from the future).
*/
invariant checkPointBlockNumberValidity(env e1)
    e1.block.number > 0 => (forall uint256 i . forall address user . to_mathint(fromBlocks[user][i]) <= to_mathint(e1.block.number))
    { 
        preserved with (env e) { 
            require e1.block.number < max_uint128 && e.block.number == e1.block.number; 
        } 
    }

/*
    @Description:
        checkpoint.fromBlock is monotonicly increasing for each user. This rule was proven inorder to assume this property on the mirrored structs and thats why it is vaccuous now.
*/
invariant blockNumberMonotonicInc(env e1)
    getFromBlockByAddressAndIndex(e1.msg.sender, e1.block.number) < getFromBlockByAddressAndIndex(e1.msg.sender, assert_uint256(e1.block.number + 1))
    { 
        preserved with (env e) { 
            requireInvariant checkPointBlockNumberValidity(e); 
        } 
    }

/*
    @Description:
        All Block Numbers Are Greater OrEqual To the Creation Block.
*/
invariant allBlockNumbersAreGreaterOrEqualToCreationBlock(address user, uint256 index)
    getFromBlockByAddressAndIndex(user, index) >= creationBlock()
    { preserved with (env e) { require e.block.number > creationBlock();} }

/*
    @Description:
        All Block Numbers Are Greater OrEqual To the Parent Snapshot Block.
*/
invariant allFromBlockAreGreaterThanParentSnapShotBlock(address user, uint256 index) 
    getFromBlockByAddressAndIndex(user, index) >= parentSnapShotBlock();

/*
    @Description:
        The balance of each user must be less or equal to the total supply.
*/
invariant balanceOfLessOrEqToTotalSpply(env e, address owner, uint blocknumber)
    balanceOfAt(e, owner, blocknumber) <= totalSupplyAt(e, blocknumber);

/*
    @Description:
        Balance of address 0 is always 0
*/
invariant ZeroAddressNoBalance(env e)
    currentContract.balanceOf(e, 0) == 0
    { 
        preserved claimTokens(address _token) with (env e1) { 
            require _token == DummyERC20;
        } 
    }

/*
    @Description:
         Cant change balances and totalSupply history.
*/
rule historyMutability(method f, address user) {
    env e1;
    env e;
    calldataarg args;

    require e1.block.number > e.block.number;

    uint256 balanceOfBefore = balanceOfAt(e, user, e.block.number);
    uint256 totalSupplyBefore = totalSupplyAt(e, e.block.number);

    f(e1, args);

    uint256 balanceOfAfter = balanceOfAt(e, user, e.block.number);
    uint256 totalSupplyAfter = totalSupplyAt(e, e.block.number);

    assert balanceOfBefore == balanceOfAfter;
    assert totalSupplyBefore == totalSupplyAfter;
}

/*
    @Description:
        Verify that there is no fee on transferFrom() (like potentially on USDT)
*/
rule noFeeOnTransferFrom(address alice, address bob, uint256 amount) {
    env e;
    require alice != bob;
    require allowance(alice, e.msg.sender) >= amount;
    requireInvariant checkPointBlockNumberValidity(e);
    requireInvariant allFromBlockAreGreaterThanParentSnapShotBlock(e.msg.sender, 0);
    requireInvariant allFromBlockAreGreaterThanParentSnapShotBlock(bob, 0);
    requireInvariant allFromBlockAreGreaterThanParentSnapShotBlock(alice, 0);
    mathint balanceBefore = currentContract.balanceOf(e, bob);
    mathint balanceAliceBefore = currentContract.balanceOf(e, alice);
    // avoid overflows
    require balanceBefore + balanceAliceBefore < max_uint128;

    bool success = transferFrom(e, alice, bob, amount);

    mathint balanceAfter = currentContract.balanceOf(e, bob);
    mathint balanceAliceAfter = currentContract.balanceOf(e, alice);

    assert success => balanceAfter == balanceBefore + amount;
    assert success => balanceAliceAfter == balanceAliceBefore - amount;
    assert !success => balanceAfter == balanceBefore;
    assert !success => balanceAliceAfter == balanceAliceBefore;
}

/*
    @Description:
        Verify that there is no fee on transfer() (like potentially on USDT)
*/
rule noFeeOnTransfer(address bob, uint256 amount) {
    env e;
    require bob != e.msg.sender;
    requireInvariant checkPointBlockNumberValidity(e);
    requireInvariant allFromBlockAreGreaterThanParentSnapShotBlock(e.msg.sender, 0);
    requireInvariant allFromBlockAreGreaterThanParentSnapShotBlock(bob, 0);
    mathint balanceSenderBefore = currentContract.balanceOf(e, e.msg.sender);
    mathint balanceBefore = currentContract.balanceOf(e, bob);
    // avoid overflows
    require balanceBefore + balanceSenderBefore < max_uint128;

    bool success = transfer(e, bob, amount);

    mathint balanceAfter = currentContract.balanceOf(e, bob);
    mathint balanceSenderAfter = currentContract.balanceOf(e, e.msg.sender);

    assert success => balanceAfter == balanceBefore + amount;
    assert success => balanceSenderAfter == balanceSenderBefore - amount;
    assert !success => balanceAfter == balanceBefore;
    assert !success => balanceSenderAfter == balanceSenderBefore;
}

/*
    @Description:
        Token transfer works correctly. Balances are updated if not reverted. 
        If reverted then the transfer amount was too high, or the recipient is 0.


    @Notes:
        This rule fails on tokens with a blacklist function, like USDC and USDT.
        The prover finds a counterexample of a reverted transfer to a blacklisted address or a transfer in a paused state.
*/
rule transferCorrect(address to, uint256 amount) {
    env e;
    require e.msg.value == 0 && e.msg.sender != 0;
    require e.msg.sender < 100;
    requireInvariant checkPointBlockNumberValidity(e);

    uint256 fromBalanceBefore = currentContract.balanceOf(e, e.msg.sender);
    uint256 toBalanceBefore = currentContract.balanceOf(e, to);
    // avoid overflows
    require fromBalanceBefore + toBalanceBefore <= max_uint128;

    bool success = transfer(e, to, amount);
    if (success) {
        if (e.msg.sender == to) {
            assert currentContract.balanceOf(e, e.msg.sender) == fromBalanceBefore;
        } else {
            assert currentContract.balanceOf(e, e.msg.sender) == assert_uint256(fromBalanceBefore - amount);
            assert currentContract.balanceOf(e, to) == assert_uint256(toBalanceBefore + amount);
        }
    } else {
        assert amount > fromBalanceBefore || to == 0;
    }
}

/*
    @Description:
        Test that transferFrom works correctly. Balances are updated if not reverted. 
        If reverted, it means the transfer amount was too high, or the recipient is 0

    @Notes:
        This rule fails on tokens with a blacklist and or pause function, like USDC and USDT.
        The prover finds a counterexample of a reverted transfer to a blacklisted address or a transfer in a paused state.
*/
rule transferFromCorrect(address from, address to, uint256 amount) {
    env e;
    require e.msg.value == 0;
    uint256 fromBalanceBefore = currentContract.balanceOf(e, from);
    uint256 toBalanceBefore = currentContract.balanceOf(e, to);
    uint256 allowanceBefore = allowance(from, e.msg.sender);
    // avoid overflows
    require fromBalanceBefore + toBalanceBefore <= max_uint128;

    bool success = transferFrom(e, from, to, amount);

    assert (success && from != to) =>
        currentContract.balanceOf(e, from) == assert_uint256(fromBalanceBefore - amount) &&
        currentContract.balanceOf(e, to) == assert_uint256(toBalanceBefore + amount) &&
        allowance(from, e.msg.sender) == assert_uint256(allowanceBefore - amount);
}

/*
    @Description:
        transferFrom should revert if and only if the amount is too high or the recipient is 0 or transfer is not enabled (if the was not made by the controller) or if the blocknumber is not valid.

    @Notes:
        Fails on tokens with pause/blacklist functions, like USDC.
*/
rule transferFromReverts(address from, address to, uint256 amount) {
    env e;
    uint256 allowanceBefore = allowance(from, e.msg.sender);
    uint256 fromBalanceBefore = currentContract.balanceOf(e, from);
    address controllerAddress = controller();
    requireInvariant allFromBlockAreGreaterThanParentSnapShotBlock(e.msg.sender, 0);
    require from != 0 && e.msg.sender != 0;
    require e.msg.value == 0;
    // avoid overflows
    require fromBalanceBefore + currentContract.balanceOf(e, to) <= max_uint128;
    bool transfersEnabled = transfersEnabled();

    transferFrom@withrevert(e, from, to, amount);

    bool didRevert = lastReverted;

    assert didRevert <=> 
           (allowanceBefore < amount && e.msg.sender != controllerAddress || amount > fromBalanceBefore || to == 0 && amount != 0 || to == currentContract && amount != 0 || !transfersEnabled && e.msg.sender != controllerAddress || parentSnapShotBlock() >= e.block.number && amount != 0); // && e.msg.sender != controllerAdress;
}

/*
    @Description:
        Contract calls don't change token total supply.

    @Notes:
        This rule should fail for any token that has functions that change totalSupply(), like mint() and burn().
        It's still important to run the rule and see if it fails in functions that _aren't_ supposed to modify totalSupply()
*/
rule NoChangeTotalSupply(method f) {
    env eTotalSupply;
    env e;
    calldataarg args;
    require doesntChangeBalance(f);
    uint256 totalSupplyBefore = currentContract.totalSupply(eTotalSupply);
    f(e, args);
    assert currentContract.totalSupply(eTotalSupply) == totalSupplyBefore;
}

/*
    @Description:
        Test that generateTokens works correctly. Balances and totalSupply are updated corrct according to the paramenters.
*/
rule integrityOfGenerateTokens(address owner, uint amount) {
    env e;
    requireInvariant checkPointBlockNumberValidity(e);
    mathint totalSupplyBefore = currentContract.totalSupply(e);
    mathint ownerBalanceBefore = currentContract.balanceOf(e, owner);

    // avoid overflows
    require totalSupplyBefore + amount < max_uint128;
    require ownerBalanceBefore + amount < max_uint128;

    bool success = generateTokens(e, owner, amount);

    mathint totalSupplyAfter = currentContract.totalSupply(e);
    mathint ownerBalanceAfter = currentContract.balanceOf(e, owner);

    assert success => (totalSupplyAfter == totalSupplyBefore + amount && ownerBalanceAfter == ownerBalanceBefore + amount);
    assert !success => (totalSupplyAfter == totalSupplyBefore && ownerBalanceAfter == ownerBalanceBefore);
}

/*
    @Description:
        Test that destroyTokens works correctly. Balances and totalSupply are updated corrct according to the paramenters.
*/
rule integrityOfDestroyTokens(address owner, uint amount) {
    env e;
    requireInvariant checkPointBlockNumberValidity(e);
    mathint totalSupplyBefore = currentContract.totalSupply(e);
    mathint ownerBalanceBefore = currentContract.balanceOf(e, owner);

    bool success = destroyTokens(e, owner, amount);

    mathint totalSupplyAfter = currentContract.totalSupply(e);
    mathint ownerBalanceAfter = currentContract.balanceOf(e, owner);

    assert success => (totalSupplyAfter == totalSupplyBefore - amount && ownerBalanceAfter == ownerBalanceBefore - amount);
    assert !success => (totalSupplyAfter == totalSupplyBefore && ownerBalanceAfter == ownerBalanceBefore);
}

/*
    @Description:
        Transfer from a to b using transfer doesn't change the balance of other addresses
*/
rule TransferDoesntChangeOtherBalances(address other, address bob, uint256 amount) {
    env e;
    require bob != e.msg.sender;
    require bob != other && e.msg.sender != other;
    requireInvariant checkPointBlockNumberValidity(e);

    mathint balanceBeforeOther = currentContract.balanceOf(e, other);

    bool success = transfer(e, bob, amount);

    assert balanceBeforeOther == to_mathint(currentContract.balanceOf(e, other));
}

/*
    @Description:
        Transfer from a to b using transferFrom doesn't change the balance of other addresses
*/
rule TransferFromDoesntChangeOtherBalances(address other, address alice, address bob, uint256 amount) {
    env e;
    require bob != alice;
    require bob != other && e.msg.sender != other && other != alice;
    requireInvariant checkPointBlockNumberValidity(e);

    mathint balanceBeforeOther = currentContract.balanceOf(e, other);

    bool success = transferFrom(e, alice, bob, amount);

    assert balanceBeforeOther == to_mathint(currentContract.balanceOf(e, other));
}


/*
    @Description:
        Allowance changes correctly as a result of calls to approve, transfer, increaseAllowance, decreaseAllowance


    @Notes:
        Some ERC20 tokens have functions like permit() that change allowance via a signature. 
        The rule will fail on such functions.
*/
rule ChangingAllowance(method f, address from, address spender) {
    uint256 allowanceBefore = allowance(from, spender);
    env e;
    if (f.selector == sig:approve(address, uint256).selector) {
        address spender_;
        uint256 amount;
        approve(e, spender_, amount);
        if (from == e.msg.sender && spender == spender_) {
            assert allowance(from, spender) == amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:transferFrom(address,address,uint256).selector) {
        address from_;
        address to;
        uint256 amount;
        transferFrom(e, from_, to, amount);
        mathint allowanceAfter = allowance(from, spender);
        if (from == from_ && spender == e.msg.sender) {
            assert from == to || allowanceBefore == max_uint256 || allowanceAfter == allowanceBefore - amount;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector) {
        address owner;
        address spender_;
        uint256 value;
        uint256 deadline;
        uint8 v;
        bytes32 r;
        bytes32 s;
        permit(e, owner, spender_, value, deadline, v, r, s);
        if (from == owner && spender == spender_) {
            assert allowance(from, spender) == value;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        }
    } else if (f.selector == sig:approveAndCall(address, uint256, bytes).selector) {
        address spender_;
        uint256 amount_;
        bytes extraData_;
        approveAndCall(e, spender_, amount_, extraData_);
        if (from == e.msg.sender && spender == spender_) {
            assert allowance(from, spender) == amount_;
        } else {
            assert allowance(from, spender) == allowanceBefore;
        } 
    } else
    {
        calldataarg args;
        f(e, args);
        assert allowance(from, spender) == allowanceBefore;
    }
}
