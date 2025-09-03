import React, { useState } from 'react';
import { VideoCameraIcon, MicrophoneIcon, ExclamationCircleIcon, CheckCircleIcon, ClockIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

const VideoTranscription = () => {
  const [tiktokUrl, setTiktokUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [processStep, setProcessStep] = useState('');
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!tiktokUrl.trim()) {
      setError('Por favor, insira uma URL do TikTok');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setProgress(0);
    setProcessStep('Validando URL...');

    try {
      // Initial progress
      setProgress(10);

      // Simulate gradual progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) return 90; // Stop at 90% until API completes
          return prev + Math.random() * 15; // Random increments
        });
      }, 800);

      // Step updates
      setTimeout(() => {
        setProcessStep('Verificando se é vídeo de influenciador...');
      }, 1000);
      
      setTimeout(() => {
        setProcessStep('Baixando vídeo...');
      }, 3000);
      
      setTimeout(() => {
        setProcessStep('Transcrevendo com OpenAI...');
      }, 5000);

      const response = await fetch('http://localhost:8000/api/v1/videos/transcribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tiktok_url: tiktokUrl
        })
      });

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Resposta da API não é um JSON válido');
      }

      const data = await response.json();
      clearInterval(progressInterval);
      setProgress(100);
      setProcessStep('Concluído!');
      setResult(data);

      if (!data.success) {
        setError(data.message);
      }
    } catch (err) {
      clearInterval(progressInterval);
      console.error('Erro:', err);
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        setError('Erro de conexão. Verifique se o backend está rodando.');
      } else if (err.message.includes('JSON')) {
        setError('Erro na resposta da API. Resposta inválida recebida.');
      } else if (err.message.includes('HTTP')) {
        setError(`Erro na API: ${err.message}`);
      } else {
        setError('Erro inesperado. Tente novamente.');
      }
    } finally {
      setLoading(false);
      if (!result) {
        setProcessStep('');
        setProgress(0);
      }
    }
  };

  const resetForm = () => {
    setTiktokUrl('');
    setResult(null);
    setError('');
    setProcessStep('');
    setProgress(0);
  };

  const copyTranscription = () => {
    if (result?.transcription) {
      navigator.clipboard.writeText(result.transcription);
      // Could add a toast notification here
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <VideoCameraIcon className="h-8 w-8 text-blue-600" />
          Transcrição de Vídeos
        </h1>
        <p className="mt-2 text-gray-600">
          Cole a URL de um vídeo do TikTok para gerar sua transcrição automaticamente
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="tiktok-url" className="block text-sm font-medium text-gray-700 mb-2">
              URL do TikTok
            </label>
            <div className="relative">
              <input
                type="url"
                id="tiktok-url"
                value={tiktokUrl}
                onChange={(e) => setTiktokUrl(e.target.value)}
                placeholder="https://www.tiktok.com/@usuario/video/123456789"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
            </div>
          </div>

          {/* Process Step Indicator */}
          {loading && processStep && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <ClockIcon className="h-5 w-5 text-blue-500 animate-pulse" />
                  <div>
                    <h3 className="text-sm font-medium text-blue-800">Processando</h3>
                    <p className="text-sm text-blue-600 mt-1">{processStep}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-lg font-bold text-blue-700">{Math.round(progress)}%</span>
                </div>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-3 shadow-inner">
                <div 
                  className={`h-3 rounded-full transition-all duration-700 ease-out ${
                    progress < 30 ? 'bg-gradient-to-r from-blue-400 to-blue-500' :
                    progress < 70 ? 'bg-gradient-to-r from-blue-500 to-indigo-500' :
                    progress < 100 ? 'bg-gradient-to-r from-indigo-500 to-purple-500' :
                    'bg-gradient-to-r from-green-500 to-emerald-500'
                  }`}
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-blue-500 mt-2">
                <span>🚀 Iniciando...</span>
                <span>✅ Concluído!</span>
              </div>
            </div>
          )}

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Processando...
                </>
              ) : (
                <>
                  <MicrophoneIcon className="h-5 w-5" />
                  Gerar Transcrição
                </>
              )}
            </button>
            
            {result && (
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Nova Busca
              </button>
            )}
          </div>
        </form>

        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <ExclamationCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Erro</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="mt-6 space-y-4">
            {/* Status Message */}
            <div className={`p-4 rounded-lg flex items-start gap-3 ${
              result.success 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-yellow-50 border border-yellow-200'
            }`}>
              <CheckCircleIcon className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
                result.success ? 'text-green-500' : 'text-yellow-500'
              }`} />
              <div>
                <h3 className={`text-sm font-medium ${
                  result.success ? 'text-green-800' : 'text-yellow-800'
                }`}>
                  Status
                </h3>
                <p className={`text-sm mt-1 ${
                  result.success ? 'text-green-700' : 'text-yellow-700'
                }`}>
                  {result.message}
                </p>
              </div>
            </div>

            {/* Video Information */}
            {result.is_influencer_video && result.video_info && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-800 mb-3">Informações do Vídeo</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-blue-700">Influenciador:</span>
                    <p className="text-blue-600">{result.eldorado_username}</p>
                  </div>
                  <div>
                    <span className="font-medium text-blue-700">TikTok:</span>
                    <p className="text-blue-600">@{result.video_info.tiktok_username}</p>
                  </div>
                  <div>
                    <span className="font-medium text-blue-700">Visualizações:</span>
                    <p className="text-blue-600">{result.video_info.view_count.toLocaleString()}</p>
                  </div>
                  <div>
                    <span className="font-medium text-blue-700">Curtidas:</span>
                    <p className="text-blue-600">{result.video_info.like_count.toLocaleString()}</p>
                  </div>
                </div>
                {result.video_info.description && (
                  <div className="mt-3">
                    <span className="font-medium text-blue-700">Descrição:</span>
                    <p className="text-blue-600 mt-1">{result.video_info.description}</p>
                  </div>
                )}
              </div>
            )}

            {/* Transcription */}
            {result.transcription && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                    <DocumentTextIcon className="h-5 w-5 text-green-600" />
                    Transcrição Completa
                  </h3>
                  <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                    {result.transcription.length} caracteres
                  </span>
                </div>
                
                <div className="bg-white rounded-lg p-6 border shadow-sm">
                  <p className="text-gray-800 leading-relaxed whitespace-pre-wrap font-medium">
                    {result.transcription}
                  </p>
                </div>
                
                <div className="flex gap-3 mt-4">
                  <button
                    onClick={copyTranscription}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <DocumentTextIcon className="h-4 w-4 mr-2" />
                    Copiar Transcrição
                  </button>
                  <button
                    onClick={() => {
                      const element = document.createElement('a');
                      const file = new Blob([result.transcription], {type: 'text/plain'});
                      element.href = URL.createObjectURL(file);
                      element.download = `transcricao-${result.video_info?.tiktok_username || 'video'}.txt`;
                      document.body.appendChild(element);
                      element.click();
                      document.body.removeChild(element);
                    }}
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                  >
                    📥 Baixar Arquivo
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoTranscription;