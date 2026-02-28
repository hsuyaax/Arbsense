type ChainInfo = {
  bsc: {
    contract_address: string;
    explorer_url: string;
    verified: boolean;
    opportunity_count: number;
    network: string;
  };
  opbnb: {
    contract_address: string;
    explorer_url: string;
    verified: boolean;
    opportunity_count: number;
    network: string;
  };
  wallet_address: string;
  wallet_balance_bsc: string;
  wallet_balance_opbnb: string;
};

export function OnChainTab({ chainInfo }: { chainInfo: ChainInfo }) {
  return (
    <div className="flex flex-col gap-6">
      {/* Chain cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/[0.12] border border-white/[0.12]">
        {/* BSC Card */}
        <div className="panel">
          <div className="panel-header">
            <span>BSC Testnet</span>
            <span>Chain ID: 97</span>
          </div>

          <div className="flex flex-col gap-4">
            <div>
              <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Contract Address</span>
              <div className="flex items-center gap-3 mt-1">
                <p className="font-mono text-[13px] text-white truncate flex-1">
                  {chainInfo.bsc.contract_address || "Not deployed"}
                </p>
                {chainInfo.bsc.explorer_url && (
                  <a
                    href={chainInfo.bsc.explorer_url}
                    target="_blank"
                    rel="noreferrer"
                    className="tag hover:border-white/40 transition-colors"
                  >
                    Explorer →
                  </a>
                )}
              </div>
            </div>

            <div className="flex gap-8">
              <div>
                <span className="font-mono text-[9px] uppercase text-muted tracking-wider">On-Chain Reports</span>
                <p className="font-mono text-2xl mt-1">{chainInfo.bsc.opportunity_count}</p>
              </div>
              <div>
                <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Status</span>
                <p className="mt-1"><span className="tag">{chainInfo.bsc.contract_address ? "Deployed" : "Pending"}</span></p>
              </div>
            </div>
          </div>
        </div>

        {/* opBNB Card */}
        <div className="panel">
          <div className="panel-header">
            <span>opBNB Testnet</span>
            <span>Chain ID: 5611</span>
          </div>

          <div className="flex flex-col gap-4">
            <div>
              <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Contract Address</span>
              <div className="flex items-center gap-3 mt-1">
                <p className="font-mono text-[13px] text-muted truncate flex-1">
                  {chainInfo.opbnb.contract_address || "Not deployed"}
                </p>
                {chainInfo.opbnb.explorer_url && (
                  <a
                    href={chainInfo.opbnb.explorer_url}
                    target="_blank"
                    rel="noreferrer"
                    className="tag hover:border-white/40 transition-colors"
                  >
                    Explorer →
                  </a>
                )}
              </div>
            </div>

            <div className="flex gap-8">
              <div>
                <span className="font-mono text-[9px] uppercase text-muted tracking-wider">On-Chain Reports</span>
                <p className="font-mono text-2xl mt-1">{chainInfo.opbnb.opportunity_count}</p>
              </div>
              <div>
                <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Status</span>
                <p className="mt-1"><span className="tag">{chainInfo.opbnb.contract_address ? "Deployed" : "Pending"}</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Wallet + Architecture */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/[0.12] border border-white/[0.12]">
        <div className="panel">
          <div className="panel-header">
            <span>Agent Wallet</span>
            <span>Signing & Gas</span>
          </div>

          <div className="flex flex-col gap-4">
            <div>
              <span className="font-mono text-[9px] uppercase text-muted tracking-wider">Address</span>
              <p className="font-mono text-[13px] text-white mt-1">
                {chainInfo.wallet_address || "Not configured"}
              </p>
            </div>

            <div className="flex gap-8">
              <div>
                <span className="font-mono text-[9px] uppercase text-muted tracking-wider">BSC Balance</span>
                <p className="font-mono text-lg mt-1">{chainInfo.wallet_balance_bsc}</p>
              </div>
              <div>
                <span className="font-mono text-[9px] uppercase text-muted tracking-wider">opBNB Balance</span>
                <p className="font-mono text-lg mt-1">{chainInfo.wallet_balance_opbnb}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span>Architecture</span>
            <span>How it works</span>
          </div>

          <div className="font-mono text-[11px] leading-[1.8] text-muted">
            <div className="flex gap-4 mb-2">
              <span className="text-white">01</span>
              <span>Agent selects top-1 opportunity per cycle</span>
            </div>
            <div className="flex gap-4 mb-2">
              <span className="text-white">02</span>
              <span>Calls reportOpportunity() on ArbSenseRegistry</span>
            </div>
            <div className="flex gap-4 mb-2">
              <span className="text-white">03</span>
              <span>Stores market pair, spread (bps), confidence (bps)</span>
            </div>
            <div className="flex gap-4 mb-2">
              <span className="text-white">04</span>
              <span>Emits OpportunityReported event for indexing</span>
            </div>
            <div className="flex gap-4">
              <span className="text-white">05</span>
              <span>Immutable on-chain proof of every discovery</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
