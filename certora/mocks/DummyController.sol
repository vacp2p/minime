// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;

contract DummyController {
    function transfer(address recipient, uint256 amount) external returns (bool) {
        return true;
    }
}