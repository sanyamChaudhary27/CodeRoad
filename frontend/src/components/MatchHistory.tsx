import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchHistoryService, type Match } from '../services/matchHistoryService';
import { matchmakingService } from '../services/matchmakingService';
import { Trophy, Target, Clock, Code, Eye, RotateCcw, Calendar, Award, X } from 'lucide-react';

interface MatchHistoryProps {
  userId: string;
  limit?: number;
}

const MatchHistory = ({ userId, limit = 20 }: MatchHistoryProps) => {
  const navigate = useNavigate();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [challengeDetails, setChallengeDetails] = useState<any>(null);
  const [loadingChallenge, setLoadingChallenge] = useState(false);

  useEffect(() => {
    fetchMatchHistory();
  }, [limit]);

  const fetchMatchHistory = async () => {
    try {
      setLoading(true);
      const data = await matchHistoryService.getMatchHistory(limit);
      setMatches(data.matches);
    } catch (error) {
      console.error('Failed to fetch match history:', error);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewMatch = async (match: Match) => {
    setSelectedMatch(match);
    setLoadingChallenge(true);
    try {
      const details = await matchHistoryService.getChallengeDetails(match.challenge_id);
      setChallengeDetails(details);
    } catch (error) {
      console.error('Failed to fetch challenge details:', error);
    } finally {
      setLoadingChallenge(false);
    }
  };

  const handleRecodeMatch = async (match: Match) => {
    try {
      const result = await matchmakingService.createPracticeMatch(
        match.difficulty_level || 'intermediate',
        match.challenge_type || 'dsa',
        match.challenge_id
      );
      
      navigate('/arena', { 
        state: { 
          matchId: result.match_id || result.id
        } 
      });
    } catch (error) {
      console.error('Failed to start recode:', error);
      alert('Failed to start recode. Please try again.');
    }
  };

  const getResultBadge = (match: Match) => {
    const result = matchHistoryService.getMatchResult(match, userId);
    
    if (result === 'ongoing') {
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-accent/20 text-accent border border-accent/30">
          In Progress
        </span>
      );
    }
    
    if (result === 'win') {
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-success/20 text-success border border-success/30 flex items-center gap-1">
          <Trophy size={12} /> Victory
        </span>
      );
    }
    
    if (result === 'loss') {
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-danger/20 text-danger border border-danger/30">
          Defeat
        </span>
      );
    }
    
    return (
      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-warning/20 text-warning border border-warning/30">
        Draw
      </span>
    );
  };

  const getDifficultyColor = (difficulty: string | null) => {
    if (!difficulty) return 'text-text-secondary';
    switch (difficulty.toLowerCase()) {
      case 'beginner': return 'text-success';
      case 'intermediate': return 'text-warning';
      case 'advanced': return 'text-danger';
      default: return 'text-text-secondary';
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatTime = (dateString: string | null) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-pulse-glow p-4 rounded-full bg-primary/20 inline-block">
          <Clock size={32} className="text-primary animate-pulse" />
        </div>
        <p className="text-text-secondary mt-4">Loading match history...</p>
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="text-center py-12 text-text-muted border border-dashed border-border-light rounded-xl">
        <Target size={48} className="mx-auto mb-4 opacity-20" />
        <p className="text-lg mb-2">No matches played yet</p>
        <p className="text-sm">Start your first match to build your history!</p>
        <button 
          onClick={() => navigate('/dashboard')}
          className="mt-6 btn btn-primary"
        >
          Enter Arena
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {matches.map((match) => {
          const opponent = matchHistoryService.getOpponent(match, userId);
          const playerScore = matchHistoryService.getPlayerScore(match, userId);
          const opponentScore = opponent ? (match.player1.player_id === userId ? match.player2_score : match.player1_score) : null;
          const isSolo = !match.player2;

          return (
            <div 
              key={match.match_id}
              className="glass-panel p-4 hover:border-primary/30 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    {getResultBadge(match)}
                    <span className={`text-xs font-semibold uppercase ${getDifficultyColor(match.difficulty_level)}`}>
                      {match.difficulty_level || 'Unknown'}
                    </span>
                    <span className="text-xs text-text-muted">
                      {isSolo ? 'Solo Practice' : '1v1 Match'}
                    </span>
                  </div>
                  
                  <h3 className="text-white font-semibold truncate mb-1">
                    {match.challenge_title || 'Untitled Challenge'}
                  </h3>
                  
                  <div className="flex items-center gap-4 text-sm text-text-secondary">
                    <span className="flex items-center gap-1">
                      <Calendar size={14} />
                      {formatDate(match.concluded_at || match.created_at)}
                    </span>
                    {match.concluded_at && (
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {formatTime(match.concluded_at)}
                      </span>
                    )}
                    {!isSolo && opponent && (
                      <span className="flex items-center gap-1">
                        <Target size={14} />
                        vs {opponent.username}
                      </span>
                    )}
                  </div>
                </div>

                {match.status === 'concluded' && (
                  <div className="flex items-center gap-2 px-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white">{typeof playerScore === 'number' ? playerScore.toFixed(1) : 0}</div>
                      <div className="text-xs text-text-muted">You</div>
                    </div>
                    {!isSolo && (
                      <>
                        <div className="text-text-muted">-</div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-white">{typeof opponentScore === 'number' ? opponentScore.toFixed(1) : 0}</div>
                          <div className="text-xs text-text-muted">{opponent?.username}</div>
                        </div>
                      </>
                    )}
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleViewMatch(match)}
                    className="btn-icon text-white group-hover:bg-primary/20 group-hover:text-primary"
                    title="View Details"
                  >
                    <Eye size={18} />
                  </button>
                  <button
                    onClick={() => handleRecodeMatch(match)}
                    className="btn-icon text-white group-hover:bg-accent/20 group-hover:text-accent"
                    title="Recode Challenge"
                  >
                    <RotateCcw size={18} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {selectedMatch && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex-center z-50 p-4 animate-fade-in">
          <div className="glass-panel max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-bg-panel/95 backdrop-blur-sm p-6 border-b border-border-light flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">{selectedMatch.challenge_title || 'Untitled Challenge'}</h2>
                <div className="flex items-center gap-3">
                  {getResultBadge(selectedMatch)}
                  <span className={`text-sm font-semibold ${getDifficultyColor(selectedMatch.difficulty_level)}`}>
                    {selectedMatch.difficulty_level || 'Unknown'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedMatch(null)}
                className="btn-icon hover:bg-danger/20 hover:text-danger"
              >
                <X size={24} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-bg-panel-light/50 p-4 rounded-xl border border-border-light text-center">
                  <Award className="text-primary mb-2 mx-auto" size={20} />
                  <p className="text-2xl font-bold text-white">
                    {matchHistoryService.getPlayerScore(selectedMatch, userId) ?? 0}
                  </p>
                  <p className="text-xs text-text-muted">Your Score</p>
                </div>
                
                {!selectedMatch.player2 ? null : (
                  <div className="bg-bg-panel-light/50 p-4 rounded-xl border border-border-light text-center">
                    <Target className="text-accent mb-2 mx-auto" size={20} />
                    <p className="text-2xl font-bold text-white">
                      {selectedMatch.player1.player_id === userId ? selectedMatch.player2_score : selectedMatch.player1_score ?? 0}
                    </p>
                    <p className="text-xs text-text-muted">Opponent Score</p>
                  </div>
                )}
                
                <div className="bg-bg-panel-light/50 p-4 rounded-xl border border-border-light text-center">
                  <Clock className="text-warning mb-2 mx-auto" size={20} />
                  <p className="text-2xl font-bold text-white">{selectedMatch.time_limit_seconds}s</p>
                  <p className="text-xs text-text-muted">Time Limit</p>
                </div>
                
                <div className="bg-bg-panel-light/50 p-4 rounded-xl border border-border-light text-center">
                  <Code className="text-success mb-2 mx-auto" size={20} />
                  <p className="text-2xl font-bold text-white">{selectedMatch.player1.submissions_count}</p>
                  <p className="text-xs text-text-muted">Submissions</p>
                </div>
              </div>

              {loadingChallenge ? (
                <div className="text-center py-8">
                  <div className="animate-pulse-glow p-4 rounded-full bg-primary/20 inline-block">
                    <Code size={24} className="text-primary animate-pulse" />
                  </div>
                  <p className="text-text-secondary mt-4">Loading challenge details...</p>
                </div>
              ) : challengeDetails ? (
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light">
                  <h3 className="text-lg font-semibold text-white mb-3">Challenge Description</h3>
                  <p className="text-text-secondary whitespace-pre-wrap">{challengeDetails.description}</p>
                  
                  {challengeDetails.examples && challengeDetails.examples.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-semibold text-white mb-2">Examples:</h4>
                      <div className="space-y-2">
                        {challengeDetails.examples.map((example: any, idx: number) => (
                          <div key={idx} className="bg-bg-panel/50 p-3 rounded-lg font-mono text-sm">
                            <div className="text-text-secondary">Input: <span className="text-white">{example.input}</span></div>
                            <div className="text-text-secondary">Output: <span className="text-success">{example.output}</span></div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}

              <div className="flex gap-3">
                <button
                  onClick={() => handleRecodeMatch(selectedMatch)}
                  className="btn btn-primary flex-1"
                >
                  <RotateCcw size={18} />
                  Recode This Challenge
                </button>
                <button
                  onClick={() => setSelectedMatch(null)}
                  className="btn btn-secondary"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MatchHistory;
