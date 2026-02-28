// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title ArbSenseRegistry
/// @notice Stores arbitrage opportunities reported by the ArbSense agent.
contract ArbSenseRegistry {
    struct Opportunity {
        string marketA;
        string marketB;
        uint256 spreadBps;
        uint256 confidenceBps;
        uint256 timestamp;
        address reporter;
    }

    Opportunity[] public opportunities;

    event OpportunityReported(
        uint256 indexed index,
        string marketA,
        string marketB,
        uint256 spreadBps,
        uint256 confidenceBps,
        uint256 timestamp,
        address indexed reporter
    );

    /// @notice Report a new arbitrage opportunity.
    function reportOpportunity(
        string calldata marketA,
        string calldata marketB,
        uint256 spreadBps,
        uint256 confidenceBps
    ) external {
        Opportunity memory entry = Opportunity({
            marketA: marketA,
            marketB: marketB,
            spreadBps: spreadBps,
            confidenceBps: confidenceBps,
            timestamp: block.timestamp,
            reporter: msg.sender
        });

        opportunities.push(entry);
        emit OpportunityReported(
            opportunities.length - 1,
            marketA,
            marketB,
            spreadBps,
            confidenceBps,
            block.timestamp,
            msg.sender
        );
    }

    /// @notice Return total number of stored opportunities.
    function getOpportunityCount() external view returns (uint256) {
        return opportunities.length;
    }

    /// @notice Return one stored opportunity by index.
    function getOpportunity(
        uint256 index
    )
        external
        view
        returns (
            string memory marketA,
            string memory marketB,
            uint256 spreadBps,
            uint256 confidenceBps,
            uint256 timestamp,
            address reporter
        )
    {
        Opportunity memory item = opportunities[index];
        return (
            item.marketA,
            item.marketB,
            item.spreadBps,
            item.confidenceBps,
            item.timestamp,
            item.reporter
        );
    }
}
