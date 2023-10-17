certoraRun certora/harness/MiniMeTokenHarness.sol certora/mocks/DummyERC20Impl.sol certora/mocks/DummyERC20ImplA.sol certora/mocks/DummyController.sol \
--verify MiniMeTokenHarness:certora/specs/MiniMeToken.spec \
--link MiniMeTokenHarness:parentToken=DummyERC20Impl \
--link MiniMeTokenHarness:controller=DummyController \
--solc solc8.18 \
--loop_iter 3 \
--optimistic_loop \
--packages @openzeppelin=node_modules/@openzeppelin \
--rule_sanity \
--msg "MiniMe Token all rules"