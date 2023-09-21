// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import { Test } from "forge-std/Test.sol";
import { Deploy } from "../../script/Deploy.s.sol";
import { DeploymentConfig } from "../../script/DeploymentConfig.s.sol";
import { Attacker } from "./Attacker.sol";
import { MiniMeToken } from "../../contracts/MiniMeToken.sol";

contract ReentrancyTest is Test {
    Attacker internal attackerController;
    MiniMeToken internal minimeToken;
    DeploymentConfig internal deploymentConfig;
    address internal deployer;
    address internal attackerEOA = makeAddr("attackerEOA");

    event Transfer(address from, address to, uint256 value);

    function setUp() public {
        Deploy deployment = new Deploy();
        (deploymentConfig,, minimeToken) = deployment.run();
        (deployer,,,,,,) = deploymentConfig.activeNetworkConfig();

        attackerController = new Attacker(attackerEOA);
    }

    function testAttack() public {
        address sender = makeAddr("sender");
        address receiver = makeAddr("receiver");
        uint256 fundsAmount = 10_000;
        uint256 sendAmount = 1000;

        // ensure `sender` has funds
        vm.prank(deployer);
        minimeToken.generateTokens(sender, fundsAmount);

        // change controller to attacker
        vm.prank(deployer);
        minimeToken.changeController(payable(address(attackerController)));

        // sender sends tokens to receiver
        vm.startPrank(sender);
        minimeToken.transfer(receiver, sendAmount);

        // after attack, sender has expected funds, and attacker has not received any funds 
        assertEq(minimeToken.balanceOf(attackerController.attackerEOA()), 0);
        assertEq(minimeToken.balanceOf(sender), fundsAmount - sendAmount);
    }
}
