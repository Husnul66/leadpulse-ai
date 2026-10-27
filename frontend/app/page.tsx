"use client";

import { useState, useEffect } from "react";
import {
  Lead,
  fetchLeads,
  createLead,
  generateMessage,
  fetchLeadMessages,
  GeneratedMessage,
} from "@/lib/api";

export default function Home() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Form states for creating a new lead
  const [companyName, setCompanyName] = useState("");
  const [companyUrl, setCompanyUrl] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // AI Generation Modal / Drawer state
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [channel, setChannel] = useState<"cold_email" | "linkedin" | "twitter_dm">("cold_email");
  const [senderName, setSenderName] = useState("");
  const [valueProposition, setValueProposition] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedMessages, setGeneratedMessages] = useState<GeneratedMessage[]>([]);
  const [activeTab, setActiveTab] = useState<"generate" | "history">("generate");

  // Load leads on mount
  const loadLeads = async () => {
    try {
      setLoading(true);
      const data = await fetchLeads();
      setLeads(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load leads. Is backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, []);

  // Handle Lead Creation
  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName || !companyUrl) return;

    try {
      setIsSubmitting(true);
      await createLead({
        company_name: companyName,
        company_url: companyUrl,
        target_audience: targetAudience || undefined,
      });
      setCompanyName("");
      setCompanyUrl("");
      setTargetAudience("");
      await loadLeads();
    } catch (err: any) {
      alert(err.message || "Failed to create lead");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle AI Message Generation
  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLead) return;

    try {
      setIsGenerating(true);
      await generateMessage(selectedLead.id, {
        outreach_channel: channel,
        sender_name: senderName.trim() || undefined,
        value_proposition: valueProposition.trim() || undefined,
      });
      // Refresh messages history for this lead
      const messages = await fetchLeadMessages(selectedLead.id);
      setGeneratedMessages(messages);
      setActiveTab("history");
      await loadLeads(); // Refresh lead status
    } catch (err: any) {
      alert(err.message || "AI generation failed");
    } finally {
      setIsGenerating(false);
    }
  };

  // Open AI Modal for a specific lead
  const openModal = async (lead: Lead) => {
    setSelectedLead(lead);
    setActiveTab("generate");
    try {
      const messages = await fetchLeadMessages(lead.id);
      setGeneratedMessages(messages);
    } catch {
      setGeneratedMessages([]);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-6 gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              LeadPulse AI
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Autonomous B2B Sales & Outreach Assistant powered by FastAPI & Google Gemini
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              System Online
            </span>
          </div>
        </header>

        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error} (Make sure your FastAPI backend is running at http://localhost:8000)
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Create Lead Form */}
          <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl h-fit">
            <h2 className="text-xl font-semibold mb-4 text-slate-200">Add New Lead</h2>
            <form onSubmit={handleCreateLead} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Corp"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Company Website / URL</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. https://acme.com"
                  value={companyUrl}
                  onChange={(e) => setCompanyUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Target Audience / ICP</label>
                <input
                  type="text"
                  placeholder="e.g. CTOs & VP of Engineering"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 transition font-medium rounded-lg text-sm shadow-lg shadow-indigo-600/25 disabled:opacity-50"
              >
                {isSubmitting ? "Saving..." : "Create Lead"}
              </button>
            </form>
          </section>

          {/* Right Column: Leads Table */}
          <section className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-slate-200">Prospect Pipeline</h2>
              <span className="text-xs text-slate-400 font-medium">{leads.length} Leads Total</span>
            </div>

            {loading ? (
              <div className="text-center py-12 text-slate-500">Loading leads...</div>
            ) : leads.length === 0 ? (
              <div className="text-center py-12 text-slate-500 border border-dashed border-slate-800 rounded-xl">
                No leads found. Add your first prospect on the left!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      <th className="pb-3 px-3">Company</th>
                      <th className="pb-3 px-3">Audience</th>
                      <th className="pb-3 px-3">Status</th>
                      <th className="pb-3 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50 text-sm">
                    {leads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3 px-3 font-medium text-slate-200">
                          <div>{lead.company_name}</div>
                          <a href={lead.company_url} target="_blank" rel="noreferrer" className="text-xs text-indigo-400 hover:underline">
                            {lead.company_url}
                          </a>
                        </td>
                        <td className="py-3 px-3 text-slate-400 text-xs">{lead.target_audience || "General B2B"}</td>
                        <td className="py-3 px-3">
                          <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            lead.status === "generated" 
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" 
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}>
                            {lead.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => openModal(lead)}
                            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded-lg text-xs font-medium transition border border-slate-700"
                          >
                            AI Studio
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

        </div>
      </div>

      {/* AI Generator Modal / Drawer */}
      {selectedLead && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-800 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-slate-100">AI Outreach Studio</h3>
                <p className="text-xs text-slate-400">Target: {selectedLead.company_name} ({selectedLead.company_url})</p>
              </div>
              <button
                onClick={() => setSelectedLead(null)}
                className="text-slate-400 hover:text-slate-200 text-sm font-bold px-2 py-1 bg-slate-800 rounded-lg"
              >
                ✕
              </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-800 px-6 bg-slate-950/50">
              <button
                onClick={() => setActiveTab("generate")}
                className={`py-3 px-4 text-sm font-medium border-b-2 transition ${
                  activeTab === "generate" ? "border-indigo-500 text-indigo-400" : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                Generate New Copy
              </button>
              <button
                onClick={() => setActiveTab("history")}
                className={`py-3 px-4 text-sm font-medium border-b-2 transition ${
                  activeTab === "history" ? "border-indigo-500 text-indigo-400" : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                Message History ({generatedMessages.length})
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              {activeTab === "generate" ? (
                <form onSubmit={handleGenerate} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Outreach Channel</label>
                    <select
                      value={channel}
                      onChange={(e) => setChannel(e.target.value as any)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                    >
                      <option value="cold_email">Cold Email (High-converting subject + body)</option>
                      <option value="linkedin">LinkedIn InMail / Connection Note</option>
                      <option value="twitter_dm">Twitter / X Direct Message</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Sender Name (Optional)</label>
                    <input
                      type="text"
                      placeholder="e.g. Alex Morgan"
                      value={senderName}
                      onChange={(e) => setSenderName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Value Proposition (Optional)</label>
                    <textarea
                      rows={2}
                      placeholder="e.g. We help B2B teams triple meeting booking rates via automated outbound personalization."
                      value={valueProposition}
                      onChange={(e) => setValueProposition(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 resize-none"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isGenerating}
                    className="w-full py-3 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 transition font-medium rounded-xl text-sm shadow-lg shadow-indigo-600/25 disabled:opacity-50"
                  >
                    {isGenerating ? "Gemini AI is crafting copy..." : "Generate AI Outreach Copy 🚀"}
                  </button>
                </form>
              ) : (
                <div className="space-y-4">
                  {generatedMessages.length === 0 ? (
                    <div className="text-center py-8 text-slate-500 text-sm">No generated messages yet for this lead.</div>
                  ) : (
                    generatedMessages.map((msg) => (
                      <div key={msg.id} className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                        <div className="flex justify-between items-center text-xs text-slate-400">
                          <span className="uppercase font-semibold tracking-wider bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded">
                            {msg.outreach_channel}
                          </span>
                          <span>{new Date(msg.created_at).toLocaleString()}</span>
                        </div>
                        <pre className="whitespace-pre-wrap font-sans text-xs text-slate-200 bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                          {msg.generated_content}
                        </pre>
                        <button
                          onClick={() => navigator.clipboard.writeText(msg.generated_content)}
                          className="text-xs text-indigo-400 hover:underline font-medium"
                        >
                          📋 Copy to Clipboard
                        </button>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

          </div>
        </div>
      )}
    </main>
  );
}