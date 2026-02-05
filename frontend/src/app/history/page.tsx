'use client';

import AppLayout from '@/components/layout/AppLayout';
import Modal from '@/components/common/Modal';
import { api } from '@/services/api';
import { ClipboardList, Search, Clock, Filter, Tag, Cpu } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

interface QueryLog {
  id: number;
  query: string;
  domain?: string;
  category?: string;
  domain_confidence?: number;
  model_name: string;
  response_time_ms?: number;
  created_at: string;
}

export default function HistoryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [items, setItems] = useState<QueryLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<QueryLog | null>(null);

  const fetchHistory = useCallback(async (search = '', domain = '') => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (domain) params.set('domain', domain);
      params.set('limit', '50');
      const data = await api.get<{ items: QueryLog[]; total: number }>(
        `/stats/queries?${params.toString()}`
      );
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch {
      setItems([]);
      setTotal(0);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleSearch = useCallback(() => {
    fetchHistory(searchQuery, domainFilter);
  }, [fetchHistory, searchQuery, domainFilter]);

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500">
        {/* Search + Filter */}
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="상담 내역 검색..."
              className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <select
              value={domainFilter}
              onChange={(e) => {
                setDomainFilter(e.target.value);
                fetchHistory(searchQuery, e.target.value);
              }}
              className="appearance-none bg-zinc-900 border border-zinc-800 rounded-xl pl-9 pr-8 py-3 text-sm text-white focus:outline-none focus:border-blue-500 transition-all cursor-pointer"
            >
              <option value="">전체 도메인</option>
              <option value="K쇼핑">K쇼핑</option>
              <option value="금융/보험">금융/보험</option>
              <option value="교통/운전면허">교통/운전면허</option>
              <option value="국민건강보험">국민건강보험</option>
              <option value="국민연금">국민연금</option>
              <option value="다산콜센터">다산콜센터</option>
              <option value="보건/의료">보건/의료</option>
              <option value="사회보장/복지">사회보장/복지</option>
              <option value="세금/관세">세금/관세</option>
              <option value="우편/택배">우편/택배</option>
              <option value="일반행정">일반행정</option>
              <option value="주택/부동산">주택/부동산</option>
              <option value="출입국/외국인">출입국/외국인</option>
              <option value="질병관리본부">질병관리본부</option>
            </select>
          </div>
        </div>

        {/* Result Count */}
        {!loading && total > 0 && (
          <p className="text-xs text-zinc-500 px-1">총 {total}건</p>
        )}

        {/* History List */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => <div key={i} className="skeleton h-20 w-full rounded-xl" />)}
          </div>
        ) : items.length > 0 ? (
          <div className="space-y-3">
            {items.map((h) => (
              <div
                key={h.id}
                onClick={() => setSelectedItem(h)}
                className="card-hover bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:bg-zinc-800/50 hover:border-zinc-700 cursor-pointer group transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white group-hover:text-blue-400 transition-colors line-clamp-2">{h.query}</p>
                    <div className="flex items-center gap-2 mt-2 flex-wrap">
                      {h.domain && (
                        <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-xs rounded border border-blue-500/20">
                          {h.domain}
                        </span>
                      )}
                      {h.category && (
                        <span className="px-2 py-0.5 bg-zinc-800 text-zinc-400 text-xs rounded border border-zinc-700">
                          {h.category}
                        </span>
                      )}
                      <span className="text-xs text-zinc-500">{h.created_at}</span>
                      {h.response_time_ms && (
                        <span className="flex items-center gap-1 text-xs text-zinc-600">
                          <Clock className="w-3 h-3" />
                          {(h.response_time_ms / 1000).toFixed(1)}s
                        </span>
                      )}
                    </div>
                  </div>
                  {h.domain_confidence != null && h.domain_confidence > 0 && (
                    <span className="text-xs text-zinc-500 ml-3 shrink-0">
                      {(h.domain_confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center mb-4 border-2 border-dashed border-zinc-800">
              <ClipboardList className="w-8 h-8 text-zinc-600" />
            </div>
            <h3 className="text-lg font-bold text-zinc-400 mb-2">상담 내역이 없습니다</h3>
            <p className="text-sm text-zinc-600">민원 상담을 시작하면 여기에 기록됩니다.</p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      <Modal open={!!selectedItem} onClose={() => setSelectedItem(null)} title="상담 상세" maxWidth="max-w-xl">
        {selectedItem && (
          <div className="space-y-5">

            {/* Query */}
            <div>
              <p className="text-xs text-zinc-500 mb-1.5 uppercase tracking-wider">민원 질문</p>
              <p className="text-sm text-white bg-zinc-900 rounded-lg p-3 border border-zinc-800 leading-relaxed">
                {selectedItem.query}
              </p>
            </div>

            {/* Classification */}
            <div>
              <p className="text-xs text-zinc-500 mb-1.5 uppercase tracking-wider">분류 결과</p>
              <div className="flex flex-wrap gap-2">
                {selectedItem.domain && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-500/10 text-blue-400 text-sm rounded-lg border border-blue-500/20">
                    <Tag className="w-3.5 h-3.5" />
                    {selectedItem.domain}
                  </span>
                )}
                {selectedItem.category && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 text-zinc-300 text-sm rounded-lg border border-zinc-700">
                    {selectedItem.category}
                  </span>
                )}
                {selectedItem.domain_confidence != null && selectedItem.domain_confidence > 0 && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 text-zinc-400 text-sm rounded-lg border border-zinc-800">
                    신뢰도 {(selectedItem.domain_confidence * 100).toFixed(1)}%
                  </span>
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-zinc-900 rounded-lg p-3 border border-zinc-800">
                <p className="text-xs text-zinc-500 mb-1">모델</p>
                <p className="text-sm text-white flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-zinc-500" />
                  {selectedItem.model_name || '-'}
                </p>
              </div>
              <div className="bg-zinc-900 rounded-lg p-3 border border-zinc-800">
                <p className="text-xs text-zinc-500 mb-1">응답 시간</p>
                <p className="text-sm text-white flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-zinc-500" />
                  {selectedItem.response_time_ms
                    ? `${(selectedItem.response_time_ms / 1000).toFixed(1)}s`
                    : '-'}
                </p>
              </div>
            </div>

            {/* Timestamp */}
            <p className="text-xs text-zinc-600 text-right">{selectedItem.created_at}</p>
          </div>
        )}
      </Modal>
    </AppLayout>
  );
}
