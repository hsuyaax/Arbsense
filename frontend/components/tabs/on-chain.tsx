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
  const bscUrl = chainInfo.bsc.explorer_url;
  const opbnbUrl = chainInfo.opbnb.explorer_url;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-white">On-Chain</h2>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="rounded-xl border border-line bg-panel p-4">
          <p className="text-sm text-slate-400">BSC Contract</p>
          {bscUrl ? (
            <a className="mono text-cyan-300 underline" href={bscUrl} target="_blank" rel="noreferrer">
              {chainInfo.bsc.contract_address}
            </a>
          ) : (
            <p className="text-slate-500">Not configured</p>
          )}
          <p className="mt-2 text-xs text-slate-400">
            {chainInfo.bsc.network} | Verified: {chainInfo.bsc.verified ? "Yes" : "No"} | Reports: {chainInfo.bsc.opportunity_count}
          </p>
        </div>
        <div className="rounded-xl border border-line bg-panel p-4">
          <p className="text-sm text-slate-400">opBNB Contract</p>
          {opbnbUrl ? (
            <a className="mono text-cyan-300 underline" href={opbnbUrl} target="_blank" rel="noreferrer">
              {chainInfo.opbnb.contract_address}
            </a>
          ) : (
            <p className="text-slate-500">Not configured</p>
          )}
          <p className="mt-2 text-xs text-slate-400">
            {chainInfo.opbnb.network} | Verified: {chainInfo.opbnb.verified ? "Yes" : "No"} | Reports: {chainInfo.opbnb.opportunity_count}
          </p>
        </div>
      </div>
      <div className="rounded-xl border border-line bg-panel p-4">
        <p className="text-sm text-slate-400">Wallet Address</p>
        <p className="mono text-slate-200">{chainInfo.wallet_address || "Not configured"}</p>
        <p className="mt-2 text-sm text-slate-300">BSC Balance: {chainInfo.wallet_balance_bsc}</p>
        <p className="text-sm text-slate-300">opBNB Balance: {chainInfo.wallet_balance_opbnb}</p>
      </div>
    </div>
  );
}
