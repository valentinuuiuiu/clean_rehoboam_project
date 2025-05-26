import React, { useState } from 'react';
import { FiBook, FiAward, FiBarChart2 } from 'react-icons/fi';

interface LessonContent {
  id: string;
  title: string;
  content: string;
  quiz: {
    question: string;
    options: string[];
    correctAnswer: number;
  }[];
}

interface UserProgress {
  completedLessons: string[];
  points: number;
  level: number;
}

const LESSONS: LessonContent[] = [
  {
    id: 'basics',
    title: 'Crypto Trading Basics',
    content: 'Learn the fundamentals of cryptocurrency trading, including key terms and concepts.',
    quiz: [
      {
        question: 'What is the main advantage of using limit orders over market orders?',
        options: [
          'Guaranteed execution',
          'Price control',
          'Faster execution',
          'Lower fees'
        ],
        correctAnswer: 1
      }
    ]
  },
  {
    id: 'risk',
    title: 'Risk Management',
    content: 'Understanding risk management strategies and position sizing in crypto trading.',
    quiz: [
      {
        question: 'What is the recommended maximum percentage of your portfolio to risk on a single trade?',
        options: [
          '50%',
          '25%',
          '1-2%',
          '10%'
        ],
        correctAnswer: 2
      }
    ]
  }
];

const GamifiedLearning = () => {
  const [currentLesson, setCurrentLesson] = useState<number>(0);
  const [showQuiz, setShowQuiz] = useState<boolean>(false);
  const [userProgress, setUserProgress] = useState<UserProgress>({
    completedLessons: [],
    points: 0,
    level: 1
  });

  const handleQuizSubmit = (answers: number[]) => {
    const lesson = LESSONS[currentLesson];
    let correctAnswers = 0;

    answers.forEach((answer, index) => {
      if (answer === lesson.quiz[index].correctAnswer) {
        correctAnswers++;
      }
    });

    const points = correctAnswers * 10;
    setUserProgress(prev => ({
      ...prev,
      points: prev.points + points,
      completedLessons: [...prev.completedLessons, lesson.id],
      level: Math.floor((prev.points + points) / 100) + 1
    }));

    setShowQuiz(false);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Trading Academy</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <FiAward className="text-yellow-500" />
            <span>Level {userProgress.level}</span>
          </div>
          <div className="flex items-center gap-2">
            <FiBarChart2 className="text-green-500" />
            <span>{userProgress.points} Points</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Lesson List */}
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-xl font-semibold mb-4">Learning Path</h3>
          <div className="space-y-4">
            {LESSONS.map((lesson, index) => (
              <div
                key={lesson.id}
                className={`p-4 rounded-lg cursor-pointer transition-all ${
                  userProgress.completedLessons.includes(lesson.id)
                    ? 'bg-green-800/50'
                    : 'bg-gray-600 hover:bg-gray-500'
                }`}
                onClick={() => setCurrentLesson(index)}
              >
                <div className="flex items-center gap-3">
                  <FiBook />
                  <div>
                    <h4 className="font-medium">{lesson.title}</h4>
                    {userProgress.completedLessons.includes(lesson.id) && (
                      <span className="text-sm text-green-400">Completed</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lesson Content */}
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-xl font-semibold mb-4">
            {LESSONS[currentLesson].title}
          </h3>
          <div className="prose prose-invert">
            <p>{LESSONS[currentLesson].content}</p>
          </div>
          
          {!showQuiz && !userProgress.completedLessons.includes(LESSONS[currentLesson].id) && (
            <button
              onClick={() => setShowQuiz(true)}
              className="mt-6 w-full bg-blue-600 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Take Quiz
            </button>
          )}

          {showQuiz && (
            <div className="mt-6 space-y-6">
              <h4 className="font-medium">Quiz</h4>
              {LESSONS[currentLesson].quiz.map((q, index) => (
                <div key={index} className="space-y-3">
                  <p>{q.question}</p>
                  <div className="grid gap-2">
                    {q.options.map((option, optIndex) => (
                      <button
                        key={optIndex}
                        onClick={() => handleQuizSubmit([optIndex])}
                        className="text-left p-3 bg-gray-600 rounded-lg hover:bg-gray-500 transition-colors"
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GamifiedLearning;
