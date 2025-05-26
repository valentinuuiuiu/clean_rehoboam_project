import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { FiBook, FiAward, FiBarChart2, FiTrendingUp, FiShield, FiDollarSign } from 'react-icons/fi';

interface Lesson {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_time: number;
  points_reward: number;
  prerequisites: string[];
  content: {
    theory: string;
    examples: string[];
    interactive_demo?: string;
  };
  quiz: {
    question: string;
    options: string[];
    correct_answer: number;
    explanation: string;
  }[];
  completed: boolean;
}

interface UserProgress {
  total_points: number;
  level: number;
  completed_lessons: string[];
  achievements: string[];
  streak_days: number;
  mastery_scores: {
    trading_basics: number;
    risk_management: number;
    technical_analysis: number;
    defi_protocols: number;
    layer2_networks: number;
  };
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  unlocked: boolean;
}

export const GamifiedLearning: React.FC = () => {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState<number[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchLearningData();
  }, []);

  const fetchLearningData = async () => {
    try {
      // Fetch lessons from your backend
      const lessonsResponse = await fetch('/api/learning/lessons');
      const lessonsData = await lessonsResponse.json();
      setLessons(lessonsData.lessons || []);

      // Fetch user progress
      const progressResponse = await fetch('/api/learning/progress');
      const progressData = await progressResponse.json();
      setUserProgress(progressData);

      // Fetch achievements
      const achievementsResponse = await fetch('/api/learning/achievements');
      const achievementsData = await achievementsResponse.json();
      setAchievements(achievementsData.achievements || []);

      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching learning data:', error);
      setIsLoading(false);
    }
  };

  const startLesson = (lesson: Lesson) => {
    setSelectedLesson(lesson);
    setCurrentQuizIndex(0);
    setQuizAnswers([]);
    setShowResults(false);
  };

  const submitQuizAnswer = (answerIndex: number) => {
    const newAnswers = [...quizAnswers];
    newAnswers[currentQuizIndex] = answerIndex;
    setQuizAnswers(newAnswers);

    if (currentQuizIndex < selectedLesson!.quiz.length - 1) {
      setCurrentQuizIndex(currentQuizIndex + 1);
    } else {
      completeLesson();
    }
  };

  const completeLesson = async () => {
    if (!selectedLesson) return;

    try {
      // Calculate score
      const correctAnswers = quizAnswers.filter((answer, index) => 
        answer === selectedLesson.quiz[index].correct_answer
      ).length;
      const score = (correctAnswers / selectedLesson.quiz.length) * 100;

      // Submit completion to backend
      const response = await fetch('/api/learning/complete-lesson', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lesson_id: selectedLesson.id,
          quiz_answers: quizAnswers,
          score: score,
          time_spent: Date.now() // You could track actual time spent
        })
      });

      if (response.ok) {
        const result = await response.json();
        setUserProgress(result.updated_progress);
        setAchievements(result.new_achievements || achievements);
        setShowResults(true);
      }
    } catch (error) {
      console.error('Error completing lesson:', error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800 border-green-200';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'advanced': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getLevelProgress = () => {
    if (!userProgress) return 0;
    const pointsForCurrentLevel = userProgress.level * 1000;
    const pointsForNextLevel = (userProgress.level + 1) * 1000;
    const progress = ((userProgress.total_points - pointsForCurrentLevel) / (pointsForNextLevel - pointsForCurrentLevel)) * 100;
    return Math.min(100, Math.max(0, progress));
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>🎓 Loading learning content...</span>
        </div>
      </Card>
    );
  }

  // Quiz View
  if (selectedLesson && !showResults) {
    const currentQuiz = selectedLesson.quiz[currentQuizIndex];
    
    return (
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>📚 {selectedLesson.title}</span>
            <Badge>Question {currentQuizIndex + 1} of {selectedLesson.quiz.length}</Badge>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <Progress value={(currentQuizIndex / selectedLesson.quiz.length) * 100} className="h-2" />
          
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
            <h3 className="font-semibold text-lg mb-4">{currentQuiz.question}</h3>
            
            <div className="space-y-3">
              {currentQuiz.options.map((option, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="w-full text-left justify-start p-4 h-auto"
                  onClick={() => submitQuizAnswer(index)}
                >
                  <span className="font-bold mr-2">{String.fromCharCode(65 + index)}.</span>
                  {option}
                </Button>
              ))}
            </div>
          </div>
          
          <div className="flex justify-between">
            <Button variant="outline" onClick={() => setSelectedLesson(null)}>
              ← Back to Lessons
            </Button>
            <span className="text-sm text-gray-600">
              🏆 {selectedLesson.points_reward} points upon completion
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Results View
  if (selectedLesson && showResults) {
    const correctAnswers = quizAnswers.filter((answer, index) => 
      answer === selectedLesson.quiz[index].correct_answer
    ).length;
    const score = (correctAnswers / selectedLesson.quiz.length) * 100;

    return (
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-center">🎉 Lesson Complete!</CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6 text-center">
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg">
            <div className="text-4xl font-bold text-green-600 mb-2">{score.toFixed(0)}%</div>
            <div className="text-lg text-green-800">
              {correctAnswers} out of {selectedLesson.quiz.length} correct
            </div>
          </div>
          
          <div className="flex justify-center space-x-8">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">+{selectedLesson.points_reward}</div>
              <div className="text-sm text-gray-600">Points Earned</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">Level {userProgress?.level}</div>
              <div className="text-sm text-gray-600">Current Level</div>
            </div>
          </div>
          
          <Button 
            className="bg-gradient-to-r from-blue-500 to-purple-600"
            onClick={() => {
              setSelectedLesson(null);
              fetchLearningData(); // Refresh data
            }}
          >
            Continue Learning 🚀
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Main Learning Dashboard
  return (
    <div className="space-y-6">
      {/* User Progress Header */}
      {userProgress && (
        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-2xl font-bold">🎓 Learning Dashboard</h2>
                <p className="text-gray-600">Master crypto trading with AI-powered education</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">Level {userProgress.level}</div>
                <div className="text-sm text-gray-600">{userProgress.total_points} points</div>
              </div>
            </div>
            
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Progress to next level</span>
                <span>{getLevelProgress().toFixed(0)}%</span>
              </div>
              <Progress value={getLevelProgress()} className="h-3" />
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <FiBook className="mx-auto text-2xl text-blue-500 mb-1" />
                <div className="font-bold">{userProgress.completed_lessons.length}</div>
                <div className="text-sm text-gray-600">Lessons</div>
              </div>
              <div className="text-center">
                <FiAward className="mx-auto text-2xl text-yellow-500 mb-1" />
                <div className="font-bold">{userProgress.achievements.length}</div>
                <div className="text-sm text-gray-600">Achievements</div>
              </div>
              <div className="text-center">
                <FiTrendingUp className="mx-auto text-2xl text-green-500 mb-1" />
                <div className="font-bold">{userProgress.streak_days}</div>
                <div className="text-sm text-gray-600">Day Streak</div>
              </div>
              <div className="text-center">
                <FiShield className="mx-auto text-2xl text-purple-500 mb-1" />
                <div className="font-bold">{userProgress.mastery_scores.risk_management.toFixed(0)}%</div>
                <div className="text-sm text-gray-600">Risk Mastery</div>
              </div>
              <div className="text-center">
                <FiDollarSign className="mx-auto text-2xl text-emerald-500 mb-1" />
                <div className="font-bold">{userProgress.mastery_scores.trading_basics.toFixed(0)}%</div>
                <div className="text-sm text-gray-600">Trading Mastery</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Available Lessons */}
      <Card>
        <CardHeader>
          <CardTitle>📚 Available Lessons</CardTitle>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {lessons.map((lesson) => (
              <Card key={lesson.id} className="border-2 hover:border-blue-300 transition-colors">
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold">{lesson.title}</h3>
                    {lesson.completed && <Badge className="bg-green-100 text-green-800">✓ Completed</Badge>}
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{lesson.description}</p>
                  
                  <div className="flex justify-between items-center mb-3">
                    <Badge className={getDifficultyColor(lesson.difficulty)}>
                      {lesson.difficulty}
                    </Badge>
                    <span className="text-sm text-gray-600">{lesson.estimated_time} min</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-blue-600">
                      🏆 {lesson.points_reward} points
                    </span>
                    <Button 
                      size="sm"
                      disabled={lesson.prerequisites.some(prereq => 
                        !userProgress?.completed_lessons.includes(prereq)
                      )}
                      onClick={() => startLesson(lesson)}
                    >
                      {lesson.completed ? 'Review' : 'Start'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Achievements */}
      {achievements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>🏆 Achievements</CardTitle>
          </CardHeader>
          
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {achievements.map((achievement) => (
                <div 
                  key={achievement.id}
                  className={`p-4 rounded-lg border-2 text-center ${
                    achievement.unlocked 
                      ? 'bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200' 
                      : 'bg-gray-50 border-gray-200 opacity-50'
                  }`}
                >
                  <div className="text-2xl mb-2">{achievement.icon}</div>
                  <div className="font-semibold text-sm">{achievement.title}</div>
                  <div className="text-xs text-gray-600 mt-1">{achievement.description}</div>
                  <div className="text-xs font-bold text-yellow-600 mt-1">
                    {achievement.points} pts
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
