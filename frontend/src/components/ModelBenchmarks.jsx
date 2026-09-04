import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Cpu, CheckCircle2, TrendingUp, Award, Layers, Sparkles, SlidersHorizontal, ShieldCheck } from 'lucide-react';
import { API_BASE_URL } from '../config';

export default function ModelBenchmarks() {
  const [benchmarks, setBenchmarks] = useState(null);
  const [loading, setLoading] = useState(true);

  // Theme detection
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'));
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/models/benchmark`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch from API');
        return res.json();
      })
      .then(data => {
        setBenchmarks(data);
        setLoading(false);
      })
      .catch(err => {
        console.warn('API fetch failed, loading local public JSON fallback...');
        fetch('/data/model_benchmarks.json')
          .then(res => res.json())
          .then(data => {
            setBenchmarks(data);
            setLoading(false);
          })
          .catch(e => console.error('Error loading fallback benchmarks:', e));
      });
  }, []);

  if (loading || !benchmarks) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-10 space-y-8 animate-pulse">
        <div className="h-10 w-72 bg-darkCard/50 rounded-xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="h-96 bg-darkCard/50 rounded-xl" />
          <div className="h-96 bg-darkCard/50 rounded-xl" />
        </div>
      </div>
    );
  }

  const salModels = benchmarks.salary_prediction.models;
  const plcModels = benchmarks.placement_prediction.models;

  // Chart data for Salary Regression
  const salaryChartData = Object.keys(salModels).map(name => ({
    name: name.replace(' Regressor', '').replace(' (Baseline)', ' (Base)'),
    r2: salModels[name].r2_mean,
    rmse: salModels[name].rmse_mean,
    mae: salModels[name].mae_mean,
    isWinner: name === benchmarks.salary_prediction.selected_model
  }));

  // Chart data for Placement Classification
  const placementChartData = Object.keys(plcModels).map(name => ({
    name: name.replace(' Classifier', '').replace(' (Baseline)', ' (Base)'),
    accuracy: Math.round(plcModels[name].accuracy_mean * 1000) / 10,
    roc_auc: Math.round(plcModels[name].roc_auc_mean * 1000) / 10,
    f1: Math.round(plcModels[name].f1_mean * 1000) / 10,
    isWinner: name === benchmarks.placement_prediction.selected_model
  }));

  const textColor = isDark ? '#a1a1aa' : '#71717a';
  const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(9,9,11,0.05)';

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-10">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-brandBlue text-xs font-bold uppercase tracking-widest mb-1.5">
            <Cpu size={14} /> ML Model Evaluation & Benchmarking
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-textMain font-sans">
            5-Fold Cross-Validation <span className="bg-gradient-to-r from-brandBlue via-brandCyan to-brandPurple bg-clip-text text-transparent">Leaderboard</span>
          </h1>
          <p className="text-textMuted text-sm mt-1.5 max-w-3xl">
            To ensure rigorous machine learning evaluation, all candidate models were tested using <strong>5-Fold Cross-Validation</strong> with feature engineering and hyperparameter tuning. No single train/test split bias.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start md:self-auto">
          <span className="inline-flex items-center gap-1.5 bg-brandSecondary border border-glassBorder text-xs text-brandBlue font-semibold uppercase px-3 py-1 rounded-full shadow-sm">
            ● 5-Fold Stratified CV
          </span>
        </div>
      </div>

      {/* Protocol Badge */}
      <div className="glass-card p-4 flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-brandBlue">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-brandBlue/10 text-brandBlue">
            <ShieldCheck size={20} />
          </div>
          <div>
            <span className="text-xs font-bold text-textMain block">Validation Protocol</span>
            <span className="text-[11px] text-textMuted">5-Fold Stratified CV • Standardized Splits • Real-World Error Tracking</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold bg-brandSecondary px-3 py-1.5 rounded-lg border border-glassBorder text-textMain">
            Dataset: 33,879 Postings
          </span>
          <span className="text-[11px] font-semibold bg-brandSecondary px-3 py-1.5 rounded-lg border border-glassBorder text-textMain">
            Students: 5,000 Profiles
          </span>
        </div>
      </div>

      {/* 1. Salary Prediction Benchmark Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-textMain flex items-center gap-2">
            <TrendingUp size={20} className="text-brandBlue" /> Salary Prediction (Regression)
          </h2>
          <span className="text-xs font-semibold text-brandSuccess bg-brandSuccess/10 border border-brandSuccess/20 px-2.5 py-1 rounded-full flex items-center gap-1">
            <CheckCircle2 size={12} /> Selected: {benchmarks.salary_prediction.selected_model}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Table Card */}
          <div className="glass-card p-6 lg:col-span-7 space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-textMuted block">Comparative Metrics (5-Fold Mean ± Std)</span>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-glassBorder text-textMuted pb-2">
                    <th className="py-2.5">Model</th>
                    <th className="py-2.5">R² Score</th>
                    <th className="py-2.5">RMSE</th>
                    <th className="py-2.5">MAE</th>
                    <th className="py-2.5 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-glassBorder">
                  {Object.keys(salModels).map(name => {
                    const m = salModels[name];
                    const isBest = name === benchmarks.salary_prediction.selected_model;
                    return (
                      <tr key={name} className={isBest ? 'bg-brandBlue/5 font-semibold' : ''}>
                        <td className="py-3 text-textMain flex items-center gap-1.5">
                          {isBest && <Sparkles size={13} className="text-brandBlue" />}
                          {name}
                        </td>
                        <td className="py-3 text-textMain font-mono">{m.r2_mean.toFixed(4)} <span className="text-[10px] text-textMuted">±{m.r2_std.toFixed(3)}</span></td>
                        <td className="py-3 text-textMain font-mono">${m.rmse_mean.toLocaleString()}</td>
                        <td className="py-3 text-textMain font-mono">${m.mae_mean.toLocaleString()}</td>
                        <td className="py-3 text-right">
                          {isBest ? (
                            <span className="text-[10px] font-bold bg-brandSuccess/15 text-brandSuccess px-2 py-0.5 rounded">Production</span>
                          ) : (
                            <span className="text-[10px] text-textMuted">Evaluated</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Empirical Range Note */}
            <div className="bg-brandSecondary/50 border border-glassBorder p-3.5 rounded-xl text-xs space-y-1">
              <span className="font-bold text-textMain flex items-center gap-1.5">
                <SlidersHorizontal size={14} className="text-brandCyan" /> Empirical Prediction Range
              </span>
              <p className="text-[11px] text-textMuted">
                Rather than assuming an unverified normal bell curve, our prediction intervals use the <strong>empirical validation MAE (±${benchmarks.salary_prediction.prediction_range.margin_usd.toLocaleString()})</strong>.
              </p>
            </div>
          </div>

          {/* Bar Chart Card */}
          <div className="glass-card p-6 lg:col-span-5 flex flex-col justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-textMuted mb-3 block">R² Score Comparison</span>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={salaryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                  <XAxis dataKey="name" stroke={textColor} tick={{ fontSize: 10 }} />
                  <YAxis stroke={textColor} tick={{ fontSize: 10 }} domain={[0.15, 0.25]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: isDark ? '#18181b' : '#fff', borderColor: 'rgba(255,255,255,0.1)', fontSize: '11px', borderRadius: '8px' }}
                    formatter={(val) => [val.toFixed(4), 'R² Score']}
                  />
                  <Bar dataKey="r2" radius={[6, 6, 0, 0]}>
                    {salaryChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.isWinner ? '#3b82f6' : isDark ? '#3f3f46' : '#cbd5e1'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <span className="text-[10px] text-textMuted text-center mt-2 block">
              Ridge with L2 regularization (α=50) achieved highest R² and sub-millisecond latency.
            </span>
          </div>

        </div>
      </div>

      {/* 2. Placement Prediction Benchmark Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-textMain flex items-center gap-2">
            <Award size={20} className="text-brandCyan" /> Placement Prediction (Classification)
          </h2>
          <span className="text-xs font-semibold text-brandSuccess bg-brandSuccess/10 border border-brandSuccess/20 px-2.5 py-1 rounded-full flex items-center gap-1">
            <CheckCircle2 size={12} /> Selected: {benchmarks.placement_prediction.selected_model}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Table Card */}
          <div className="glass-card p-6 lg:col-span-7 space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-textMuted block">Comparative Metrics (5-Fold Stratified CV)</span>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-glassBorder text-textMuted pb-2">
                    <th className="py-2.5">Model</th>
                    <th className="py-2.5">Accuracy</th>
                    <th className="py-2.5">F1-Score</th>
                    <th className="py-2.5">ROC-AUC</th>
                    <th className="py-2.5 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-glassBorder">
                  {Object.keys(plcModels).map(name => {
                    const m = plcModels[name];
                    const isBest = name === benchmarks.placement_prediction.selected_model;
                    return (
                      <tr key={name} className={isBest ? 'bg-brandCyan/5 font-semibold' : ''}>
                        <td className="py-3 text-textMain flex items-center gap-1.5">
                          {isBest && <Sparkles size={13} className="text-brandCyan" />}
                          {name}
                        </td>
                        <td className="py-3 text-textMain font-mono">{(m.accuracy_mean * 100).toFixed(2)}%</td>
                        <td className="py-3 text-textMain font-mono">{m.f1_mean.toFixed(4)}</td>
                        <td className="py-3 text-textMain font-mono font-bold text-brandCyan">{m.roc_auc_mean.toFixed(4)}</td>
                        <td className="py-3 text-right">
                          {isBest ? (
                            <span className="text-[10px] font-bold bg-brandSuccess/15 text-brandSuccess px-2 py-0.5 rounded">Production</span>
                          ) : (
                            <span className="text-[10px] text-textMuted">Evaluated</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Rationale note */}
            <div className="bg-brandSecondary/50 border border-glassBorder p-3.5 rounded-xl text-xs space-y-1">
              <span className="font-bold text-textMain flex items-center gap-1.5">
                <Layers size={14} className="text-brandBlue" /> Why Random Forest Won
              </span>
              <p className="text-[11px] text-textMuted">
                Random Forest increased ROC-AUC from <strong>0.8673 to 0.9063</strong> over the baseline Decision Tree, generating smooth, calibrated probabilities across all simulator ranges without sharp threshold artifacts.
              </p>
            </div>
          </div>

          {/* Bar Chart Card */}
          <div className="glass-card p-6 lg:col-span-5 flex flex-col justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-textMuted mb-3 block">ROC-AUC Score Comparison</span>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={placementChartData} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                  <XAxis dataKey="name" stroke={textColor} tick={{ fontSize: 10 }} />
                  <YAxis stroke={textColor} tick={{ fontSize: 10 }} domain={[80, 95]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: isDark ? '#18181b' : '#fff', borderColor: 'rgba(255,255,255,0.1)', fontSize: '11px', borderRadius: '8px' }}
                    formatter={(val) => [`${val}%`, 'ROC-AUC Score']}
                  />
                  <Bar dataKey="roc_auc" radius={[6, 6, 0, 0]}>
                    {placementChartData.map((entry, index) => (
                      <Cell key={`cell-plc-${index}`} fill={entry.isWinner ? '#06b6d4' : isDark ? '#3f3f46' : '#cbd5e1'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <span className="text-[10px] text-textMuted text-center mt-2 block">
              Random Forest provides a +3.9% boost in ranking discriminability (ROC-AUC).
            </span>
          </div>

        </div>
      </div>

    </div>
  );
}
