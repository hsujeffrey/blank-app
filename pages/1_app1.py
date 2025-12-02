import React, { useState } from 'react';
import { Upload, Plus, Trash2, Download, AlertCircle } from 'lucide-react';

const MarketingClassifier = () => {
  const [data, setData] = useState([]);
  const [dictionaries, setDictionaries] = useState({
    urgency_marketing: [
      'limited', 'limited time', 'limited run', 'limited edition', 'order now',
      'last chance', 'hurry', 'while supplies last', "before they're gone",
      'selling out', 'selling fast', 'act now', "don't wait", 'today only',
      'expires soon', 'final hours', 'almost gone'
    ],
    exclusive_marketing: [
      'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
      'members only', 'vip', 'special access', 'invitation only',
      'premium', 'privileged', 'limited access', 'select customers',
      'insider', 'private sale', 'early access'
    ]
  });
  const [results, setResults] = useState(null);
  const [newTactic, setNewTactic] = useState('');
  const [newKeyword, setNewKeyword] = useState({});
  const [editingKeyword, setEditingKeyword] = useState({});

  const parseCSV = (text) => {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    return lines.slice(1).map((line, index) => {
      const values = line.split(',').map(v => v.trim());
      const obj = {};
      headers.forEach((header, i) => {
        obj[header] = values[i] || '';
      });
      obj._index = index;
      return obj;
    });
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const parsedData = parseCSV(e.target.result);
        setData(parsedData);
        setResults(null);
      };
      reader.readAsText(file);
    }
  };

  const classifyStatement = (text) => {
    if (!text) return {};
    
    const textLower = text.toLowerCase();
    const results = {};
    
    Object.entries(dictionaries).forEach(([tactic, keywords]) => {
      const matches = keywords.filter(keyword => 
        textLower.includes(keyword.toLowerCase())
      );
      
      results[tactic] = {
        present: matches.length > 0,
        count: matches.length,
        matches: matches
      };
    });
    
    return results;
  };

  const runClassification = () => {
    if (data.length === 0) return;
    
    const statementColumn = Object.keys(data[0]).find(key => 
      key.toLowerCase().includes('statement') || key.toLowerCase().includes('text')
    );
    
    const classified = data.map(row => {
      const classification = classifyStatement(row[statementColumn]);
      return {
        ...row,
        classification
      };
    });
    
    setResults(classified);
  };

  const addTactic = () => {
    if (newTactic && !dictionaries[newTactic]) {
      setDictionaries({
        ...dictionaries,
        [newTactic]: []
      });
      setNewTactic('');
    }
  };

  const removeTactic = (tactic) => {
    const newDict = { ...dictionaries };
    delete newDict[tactic];
    setDictionaries(newDict);
  };

  const addKeyword = (tactic) => {
    const keyword = newKeyword[tactic];
    if (keyword && keyword.trim()) {
      setDictionaries({
        ...dictionaries,
        [tactic]: [...dictionaries[tactic], keyword.trim()]
      });
      setNewKeyword({ ...newKeyword, [tactic]: '' });
    }
  };

  const removeKeyword = (tactic, keyword) => {
    setDictionaries({
      ...dictionaries,
      [tactic]: dictionaries[tactic].filter(k => k !== keyword)
    });
  };

  const downloadResults = () => {
    if (!results) return;
    
    const statementColumn = Object.keys(results[0]).find(key => 
      key.toLowerCase().includes('statement') || key.toLowerCase().includes('text')
    );
    
    const headers = [
      ...Object.keys(results[0]).filter(k => k !== 'classification' && k !== '_index'),
      ...Object.keys(dictionaries).flatMap(tactic => [
        `${tactic}_present`,
        `${tactic}_count`,
        `${tactic}_matches`
      ])
    ];
    
    const rows = results.map(row => {
      const baseData = Object.keys(row)
        .filter(k => k !== 'classification' && k !== '_index')
        .map(k => `"${row[k]}"`);
      
      const tacticData = Object.keys(dictionaries).flatMap(tactic => {
        const classification = row.classification[tactic] || {};
        return [
          classification.present ? 'true' : 'false',
          classification.count || 0,
          `"${(classification.matches || []).join(', ')}"`
        ];
      });
      
      return [...baseData, ...tacticData].join(',');
    });
    
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'classified_data.csv';
    a.click();
  };

  const getStats = () => {
    if (!results) return null;
    
    const stats = {};
    Object.keys(dictionaries).forEach(tactic => {
      const count = results.filter(row => 
        row.classification[tactic]?.present
      ).length;
      stats[tactic] = {
        count,
        percentage: ((count / results.length) * 100).toFixed(1)
      };
    });
    
    const anyTactic = results.filter(row =>
      Object.keys(dictionaries).some(tactic =>
        row.classification[tactic]?.present
      )
    ).length;
    
    return { tactics: stats, total: results.length, anyTactic };
  };

  const stats = getStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Marketing Tactics Classifier</h1>
        <p className="text-gray-600 mb-8">Upload your dataset and customize dictionaries to classify marketing tactics</p>
        
        {/* File Upload */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Upload size={20} />
            Upload Dataset
          </h2>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {data.length > 0 && (
            <p className="mt-2 text-green-600 text-sm">✓ {data.length} rows loaded</p>
          )}
        </div>

        {/* Dictionary Management */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Marketing Tactic Dictionaries</h2>
          
          {/* Add New Tactic */}
          <div className="flex gap-2 mb-6">
            <input
              type="text"
              value={newTactic}
              onChange={(e) => setNewTactic(e.target.value)}
              placeholder="New tactic name (e.g., scarcity_marketing)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={addTactic}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus size={16} />
              Add Tactic
            </button>
          </div>

          {/* Existing Tactics */}
          <div className="space-y-4">
            {Object.entries(dictionaries).map(([tactic, keywords]) => (
              <div key={tactic} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-semibold text-gray-800">{tactic}</h3>
                  <button
                    onClick={() => removeTactic(tactic)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={newKeyword[tactic] || ''}
                    onChange={(e) => setNewKeyword({ ...newKeyword, [tactic]: e.target.value })}
                    placeholder="Add keyword..."
                    className="flex-1 px-3 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && addKeyword(tactic)}
                  />
                  <button
                    onClick={() => addKeyword(tactic)}
                    className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    Add
                  </button>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  {keywords.map((keyword, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm flex items-center gap-2"
                    >
                      {keyword}
                      <button
                        onClick={() => removeKeyword(tactic, keyword)}
                        className="hover:text-red-600"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Run Classification */}
        {data.length > 0 && (
          <button
            onClick={runClassification}
            className="w-full mb-6 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold text-lg"
          >
            Run Classification
          </button>
        )}

        {/* Results */}
        {results && (
          <>
            {/* Statistics */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4">Classification Summary</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                {Object.entries(stats.tactics).map(([tactic, data]) => (
                  <div key={tactic} className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">{tactic}</div>
                    <div className="text-2xl font-bold text-gray-800">
                      {data.count}/{stats.total}
                    </div>
                    <div className="text-sm text-gray-600">{data.percentage}%</div>
                  </div>
                ))}
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Statements with any tactic</div>
                <div className="text-2xl font-bold text-gray-800">{stats.anyTactic}/{stats.total}</div>
              </div>
            </div>

            {/* Detailed Results */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Detailed Results</h2>
                <button
                  onClick={downloadResults}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Download size={16} />
                  Download CSV
                </button>
              </div>
              
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {results.map((row, idx) => {
                  const statementColumn = Object.keys(row).find(key => 
                    key.toLowerCase().includes('statement') || key.toLowerCase().includes('text')
                  );
                  
                  return (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4">
                      <div className="font-semibold text-gray-800 mb-2">
                        {row.ID || `Row ${idx + 1}`}
                      </div>
                      <div className="text-gray-600 mb-3 italic">"{row[statementColumn]}"</div>
                      <div className="space-y-1">
                        {Object.entries(dictionaries).map(([tactic]) => {
                          const classification = row.classification[tactic];
                          return (
                            <div key={tactic} className="text-sm">
                              {classification?.present ? (
                                <div className="text-green-700">
                                  ✓ {tactic}: {classification.matches.join(', ')}
                                </div>
                              ) : (
                                <div className="text-gray-400">
                                  ✗ {tactic}: No matches
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {/* Help */}
        {data.length === 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
            <AlertCircle className="text-blue-600 flex-shrink-0" size={20} />
            <div className="text-sm text-gray-700">
              <strong>Getting Started:</strong> Upload a CSV file with a "Statement" or "Text" column containing the text you want to classify. Then customize the dictionaries above and run the classification.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketingClassifier;
