"use client";

import { useCallback, useEffect, useState } from "react";

// ── Types ────────────────────────────────────────────────────────

type Bet = {
  id: string;
  title: string;
  description: string;
  category: "habit" | "fun";
  optionA: string;
  optionB: string;
  poolA: number;
  poolB: number;
  deadline: string;
  status: "open" | "resolved";
};

type WalletState = {
  address: string;
  balance: string;
  chainId: number;
  connected: boolean;
};

// ── BSC Testnet config ───────────────────────────────────────────

const BSC_TESTNET = {
  chainId: "0x61", // 97
  chainName: "BNB Smart Chain Testnet",
  rpcUrls: ["https://data-seed-prebsc-1-s1.bnbchain.org:8545"],
  blockExplorerUrls: ["https://testnet.bscscan.com"],
  nativeCurrency: { name: "tBNB", symbol: "tBNB", decimals: 18 },
};

// ── Seed bets ────────────────────────────────────────────────────

const SEED_BETS: Bet[] = [
  {
    id: "habit-gym-5d",
    title: "Will I hit the gym 5 days this week?",
    description: "Stake tBNB on your discipline. Resolves Sunday midnight.",
    category: "habit",
    optionA: "YES — I will",
    optionB: "NO — I won't",
    poolA: 0.05,
    poolB: 0.02,
    deadline: "2026-03-07",
    status: "open",
  },
  {
    id: "habit-no-sugar-7d",
    title: "Zero sugar for 7 straight days?",
    description: "Put money where your mouth is. No sugar, no cheat days.",
    category: "habit",
    optionA: "YES — Clean week",
    optionB: "NO — Will break",
    poolA: 0.03,
    poolB: 0.04,
    deadline: "2026-03-07",
    status: "open",
  },
  {
    id: "habit-read-30min",
    title: "Read 30 min every day this week?",
    description: "Bet on building a reading habit. No audiobooks.",
    category: "habit",
    optionA: "YES — Every day",
    optionB: "NO — Will skip",
    poolA: 0.02,
    poolB: 0.03,
    deadline: "2026-03-07",
    status: "open",
  },
  {
    id: "habit-wake-6am",
    title: "Wake up before 6 AM for 5 days?",
    description: "Early bird gets the tBNB. Alarm proof required.",
    category: "habit",
    optionA: "YES — Early bird",
    optionB: "NO — Snooze king",
    poolA: 0.04,
    poolB: 0.02,
    deadline: "2026-03-07",
    status: "open",
  },
  {
    id: "fun-vlad-lucas-tower",
    title: "Vlad vs Lucas: Water Bottle Tower Showdown",
    description: "Who knocks down the water bottle tower first? Judges decide. Place your bet now.",
    category: "fun",
    optionA: "VLAD wins",
    optionB: "LUCAS wins",
    poolA: 0.06,
    poolB: 0.08,
    deadline: "2026-03-01",
    status: "open",
  },
  {
    id: "fun-coding-race",
    title: "Who ships the feature first?",
    description: "Dev A vs Dev B — first to push a working PR wins the pot.",
    category: "fun",
    optionA: "Dev A ships first",
    optionB: "Dev B ships first",
    poolA: 0.03,
    poolB: 0.03,
    deadline: "2026-03-02",
    status: "open",
  },
  {
    id: "fun-spicy-challenge",
    title: "Can Vlad finish the Carolina Reaper wing?",
    description: "One wing. No milk for 5 minutes. Judges: Lucas & the crowd.",
    category: "fun",
    optionA: "YES — He survives",
    optionB: "NO — Taps out",
    poolA: 0.02,
    poolB: 0.07,
    deadline: "2026-03-01",
    status: "open",
  },
];

// ── Helpers ──────────────────────────────────────────────────────

function getEthereum(): any {
  if (typeof window !== "undefined") {
    return (window as any).ethereum;
  }
  return null;
}

// ── Component ────────────────────────────────────────────────────

export function FunBetsTab() {
  const [wallet, setWallet] = useState<WalletState>({
    address: "",
    balance: "0",
    chainId: 0,
    connected: false,
  });
  const [bets, setBets] = useState<Bet[]>(SEED_BETS);
  const [pendingTx, setPendingTx] = useState<string | null>(null);
  const [lastTxHash, setLastTxHash] = useState<string>("");
  const [betAmounts, setBetAmounts] = useState<Record<string, string>>({});
  const [customBet, setCustomBet] = useState({ title: "", optionA: "", optionB: "", category: "fun" as "fun" | "habit" });

  // ── Wallet connect ──────────────────────────────────────────

  const connectWallet = useCallback(async () => {
    const eth = getEthereum();
    if (!eth) {
      alert("MetaMask not detected. Install MetaMask to place bets.");
      return;
    }

    try {
      const accounts: string[] = await eth.request({ method: "eth_requestAccounts" });
      const chainId = parseInt(await eth.request({ method: "eth_chainId" }), 16);

      // Switch to BSC Testnet if needed
      if (chainId !== 97) {
        try {
          await eth.request({
            method: "wallet_switchEthereumChain",
            params: [{ chainId: BSC_TESTNET.chainId }],
          });
        } catch (switchErr: any) {
          if (switchErr.code === 4902) {
            await eth.request({
              method: "wallet_addEthereumChain",
              params: [BSC_TESTNET],
            });
          }
        }
      }

      const balHex: string = await eth.request({
        method: "eth_getBalance",
        params: [accounts[0], "latest"],
      });
      const balEth = parseInt(balHex, 16) / 1e18;

      setWallet({
        address: accounts[0],
        balance: balEth.toFixed(4),
        chainId: 97,
        connected: true,
      });
    } catch (err) {
      console.error("Wallet connect failed:", err);
    }
  }, []);

  // Listen for account / chain changes
  useEffect(() => {
    const eth = getEthereum();
    if (!eth) return;

    const onAccounts = (accs: string[]) => {
      if (accs.length === 0) {
        setWallet((w) => ({ ...w, connected: false, address: "" }));
      } else {
        setWallet((w) => ({ ...w, address: accs[0] }));
      }
    };
    const onChain = () => connectWallet();

    eth.on("accountsChanged", onAccounts);
    eth.on("chainChanged", onChain);
    return () => {
      eth.removeListener("accountsChanged", onAccounts);
      eth.removeListener("chainChanged", onChain);
    };
  }, [connectWallet]);

  // ── Place bet (real on-chain tx) ────────────────────────────

  const placeBet = async (betId: string, side: "A" | "B") => {
    if (!wallet.connected) {
      await connectWallet();
      return;
    }

    const amount = parseFloat(betAmounts[betId] || "0.001");
    if (amount <= 0 || amount > 1) {
      alert("Bet amount must be between 0.001 and 1 tBNB");
      return;
    }

    const eth = getEthereum();
    if (!eth) return;

    setPendingTx(betId);
    try {
      // Send real tBNB to a burn-ish address as the "bet pool"
      // In production this would be a proper betting contract
      const weiHex = "0x" + Math.floor(amount * 1e18).toString(16);

      // Use the ArbSense contract address as the bet pool recipient
      const txHash: string = await eth.request({
        method: "eth_sendTransaction",
        params: [
          {
            from: wallet.address,
            to: "0x7Ba8FA52dAEd1c1Ea1acEB26E52339946458DeDa",
            value: weiHex,
            data: "0x" + Buffer.from(`bet:${betId}:${side}`, "utf-8").toString("hex"),
          },
        ],
      });

      setLastTxHash(txHash);

      // Update local pool
      setBets((prev) =>
        prev.map((b) => {
          if (b.id !== betId) return b;
          return side === "A"
            ? { ...b, poolA: b.poolA + amount }
            : { ...b, poolB: b.poolB + amount };
        })
      );

      // Refresh balance
      const balHex: string = await eth.request({
        method: "eth_getBalance",
        params: [wallet.address, "latest"],
      });
      setWallet((w) => ({ ...w, balance: (parseInt(balHex, 16) / 1e18).toFixed(4) }));
    } catch (err: any) {
      if (err.code !== 4001) {
        console.error("Tx failed:", err);
        alert("Transaction failed: " + (err.message || "Unknown error"));
      }
    } finally {
      setPendingTx(null);
    }
  };

  // ── Create custom bet ───────────────────────────────────────

  const createCustomBet = () => {
    if (!customBet.title || !customBet.optionA || !customBet.optionB) return;
    const newBet: Bet = {
      id: `custom-${Date.now()}`,
      title: customBet.title,
      description: "Custom bet created by you.",
      category: customBet.category,
      optionA: customBet.optionA,
      optionB: customBet.optionB,
      poolA: 0,
      poolB: 0,
      deadline: "2026-03-07",
      status: "open",
    };
    setBets((prev) => [newBet, ...prev]);
    setCustomBet({ title: "", optionA: "", optionB: "", category: "fun" });
  };

  // ── Render ──────────────────────────────────────────────────

  const habitBets = bets.filter((b) => b.category === "habit");
  const funBets = bets.filter((b) => b.category === "fun");

  return (
    <div className="flex flex-col gap-6">
      {/* Wallet Bar */}
      <div className="panel">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <span className={`w-2 h-2 rounded-full ${wallet.connected ? "bg-green-400" : "bg-neutral-600"}`} />
            {wallet.connected ? (
              <div className="flex items-center gap-6">
                <span className="font-mono text-[13px] text-white">
                  {wallet.address.slice(0, 6)}...{wallet.address.slice(-4)}
                </span>
                <span className="font-mono text-[13px] text-muted">{wallet.balance} tBNB</span>
                <span className="tag">BSC Testnet</span>
              </div>
            ) : (
              <span className="font-mono text-[13px] text-muted">Wallet not connected</span>
            )}
          </div>
          <button
            onClick={connectWallet}
            className="bg-white text-[#030303] border-none px-6 py-2.5 font-mono text-[12px] font-medium cursor-pointer hover:bg-neutral-200 transition-all"
          >
            {wallet.connected ? "Connected" : "Connect Wallet"}
          </button>
        </div>
        {lastTxHash && (
          <div className="mt-4 pt-4 border-t border-white/[0.06] flex items-center gap-3">
            <span className="font-mono text-[10px] text-muted uppercase">Last Tx:</span>
            <a
              href={`https://testnet.bscscan.com/tx/${lastTxHash}`}
              target="_blank"
              rel="noreferrer"
              className="font-mono text-[12px] text-white hover:underline"
            >
              {lastTxHash.slice(0, 14)}...{lastTxHash.slice(-8)}
            </a>
            <span className="tag">Confirmed</span>
          </div>
        )}
      </div>

      {/* Create Custom Bet */}
      <div className="panel">
        <div className="panel-header">
          <span>Create a Bet</span>
          <span>Custom</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="font-mono text-[9px] uppercase text-muted tracking-wider">What are you betting on?</label>
            <input
              type="text"
              value={customBet.title}
              onChange={(e) => setCustomBet((c) => ({ ...c, title: e.target.value }))}
              placeholder="e.g., Who eats more pizza slices?"
              className="w-full mt-1 bg-transparent border border-white/[0.12] px-3 py-2 font-mono text-[13px] text-white placeholder:text-neutral-700 outline-none focus:border-white/40"
            />
          </div>
          <div>
            <label className="font-mono text-[9px] uppercase text-muted tracking-wider">Option A</label>
            <input
              type="text"
              value={customBet.optionA}
              onChange={(e) => setCustomBet((c) => ({ ...c, optionA: e.target.value }))}
              placeholder="e.g., Vlad"
              className="w-full mt-1 bg-transparent border border-white/[0.12] px-3 py-2 font-mono text-[13px] text-white placeholder:text-neutral-700 outline-none focus:border-white/40"
            />
          </div>
          <div>
            <label className="font-mono text-[9px] uppercase text-muted tracking-wider">Option B</label>
            <input
              type="text"
              value={customBet.optionB}
              onChange={(e) => setCustomBet((c) => ({ ...c, optionB: e.target.value }))}
              placeholder="e.g., Lucas"
              className="w-full mt-1 bg-transparent border border-white/[0.12] px-3 py-2 font-mono text-[13px] text-white placeholder:text-neutral-700 outline-none focus:border-white/40"
            />
          </div>
        </div>
        <div className="flex items-center gap-4 mt-4">
          <div className="flex gap-2">
            {(["fun", "habit"] as const).map((cat) => (
              <button
                key={cat}
                onClick={() => setCustomBet((c) => ({ ...c, category: cat }))}
                className={`font-mono text-[11px] px-3 py-1 border cursor-pointer transition-all ${
                  customBet.category === cat
                    ? "border-white text-white bg-white/10"
                    : "border-white/[0.12] text-muted bg-transparent hover:border-white/40"
                }`}
              >
                {cat.toUpperCase()}
              </button>
            ))}
          </div>
          <button
            onClick={createCustomBet}
            className="bg-white text-[#030303] border-none px-5 py-1.5 font-mono text-[11px] font-medium cursor-pointer hover:bg-neutral-200 transition-all ml-auto"
          >
            + Create Bet
          </button>
        </div>
      </div>

      {/* Habit Builder Bets */}
      <div className="panel">
        <div className="panel-header">
          <span>Habit Builder — Bet on Yourself</span>
          <span>{habitBets.length} active</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/[0.06]">
          {habitBets.map((bet) => (
            <BetCard
              key={bet.id}
              bet={bet}
              amount={betAmounts[bet.id] || "0.001"}
              onAmountChange={(v) => setBetAmounts((prev) => ({ ...prev, [bet.id]: v }))}
              onBet={(side) => placeBet(bet.id, side)}
              pending={pendingTx === bet.id}
              walletConnected={wallet.connected}
            />
          ))}
        </div>
      </div>

      {/* Fun Bets */}
      <div className="panel">
        <div className="panel-header">
          <span>Fun Bets — Compete with Friends</span>
          <span>{funBets.length} active</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/[0.06]">
          {funBets.map((bet) => (
            <BetCard
              key={bet.id}
              bet={bet}
              amount={betAmounts[bet.id] || "0.001"}
              onAmountChange={(v) => setBetAmounts((prev) => ({ ...prev, [bet.id]: v }))}
              onBet={(side) => placeBet(bet.id, side)}
              pending={pendingTx === bet.id}
              walletConnected={wallet.connected}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Bet Card ─────────────────────────────────────────────────────

function BetCard({
  bet,
  amount,
  onAmountChange,
  onBet,
  pending,
  walletConnected,
}: {
  bet: Bet;
  amount: string;
  onAmountChange: (v: string) => void;
  onBet: (side: "A" | "B") => void;
  pending: boolean;
  walletConnected: boolean;
}) {
  const totalPool = bet.poolA + bet.poolB;
  const pctA = totalPool > 0 ? (bet.poolA / totalPool) * 100 : 50;
  const pctB = 100 - pctA;

  return (
    <div className="p-6 bg-panel flex flex-col gap-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="tag">{bet.category}</span>
          <span className="tag">{bet.status}</span>
        </div>
        <p className="text-[15px] text-white font-normal leading-snug mt-2">{bet.title}</p>
        <p className="font-mono text-[11px] text-neutral-600 mt-1">{bet.description}</p>
      </div>

      {/* Pool visualization */}
      <div>
        <div className="flex justify-between font-mono text-[10px] text-muted mb-1">
          <span>{bet.optionA} ({pctA.toFixed(0)}%)</span>
          <span>{bet.optionB} ({pctB.toFixed(0)}%)</span>
        </div>
        <div className="h-1.5 bg-white/[0.06] flex overflow-hidden">
          <div className="bg-white/80 transition-all" style={{ width: `${pctA}%` }} />
          <div className="bg-white/20 transition-all" style={{ width: `${pctB}%` }} />
        </div>
        <div className="flex justify-between font-mono text-[10px] text-neutral-700 mt-1">
          <span>{bet.poolA.toFixed(3)} tBNB</span>
          <span>{bet.poolB.toFixed(3)} tBNB</span>
        </div>
      </div>

      {/* Bet controls */}
      <div className="flex items-center gap-2">
        <input
          type="number"
          step="0.001"
          min="0.001"
          max="1"
          value={amount}
          onChange={(e) => onAmountChange(e.target.value)}
          className="w-24 bg-transparent border border-white/[0.12] px-2 py-1.5 font-mono text-[12px] text-white outline-none focus:border-white/40"
        />
        <span className="font-mono text-[10px] text-muted">tBNB</span>
        <div className="flex gap-2 ml-auto">
          <button
            onClick={() => onBet("A")}
            disabled={pending}
            className="bg-white text-[#030303] border-none px-4 py-1.5 font-mono text-[11px] font-medium cursor-pointer hover:bg-neutral-200 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {pending ? "..." : "Bet A"}
          </button>
          <button
            onClick={() => onBet("B")}
            disabled={pending}
            className="bg-transparent text-white border border-white/[0.12] px-4 py-1.5 font-mono text-[11px] cursor-pointer hover:border-white/40 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {pending ? "..." : "Bet B"}
          </button>
        </div>
      </div>

      {!walletConnected && (
        <p className="font-mono text-[10px] text-neutral-700">Connect wallet to place bets</p>
      )}
    </div>
  );
}
