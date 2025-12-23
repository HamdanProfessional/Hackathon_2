"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Play, Pause, RotateCcw, SkipForward, Clock } from "lucide-react";
import { Progress } from "@/components/ui/progress";

type TimerMode = 'work' | 'shortBreak' | 'longBreak';

const TIMER_CONFIG = {
  work: 25 * 60,      // 25 minutes
  shortBreak: 5 * 60, // 5 minutes
  longBreak: 15 * 60  // 15 minutes
};

export function PomodoroTimer({ taskId, taskTitle }: { taskId?: number; taskTitle?: string }) {
  const [mode, setMode] = useState<TimerMode>('work');
  const [timeLeft, setTimeLeft] = useState(TIMER_CONFIG.work);
  const [isActive, setIsActive] = useState(false);
  const [sessionsCompleted, setSessionsCompleted] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load sessions from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('pomodoroSessions');
      if (saved) {
        const parsed = JSON.parse(saved);
        // Reset if it's a new day
        const today = new Date().toDateString();
        if (parsed.date === today) {
          setSessionsCompleted(parsed.count);
        } else {
          localStorage.setItem('pomodoroSessions', JSON.stringify({ date: today, count: 0 }));
        }
      }
    }
  }, []);

  // Save sessions to localStorage whenever they change
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const today = new Date().toDateString();
      localStorage.setItem('pomodoroSessions', JSON.stringify({ date: today, count: sessionsCompleted }));
    }
  }, [sessionsCompleted]);

  useEffect(() => {
    if (isActive && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && isActive) {
      handleTimerComplete();
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isActive, timeLeft]);

  const handleTimerComplete = () => {
    setIsActive(false);

    // Play notification sound (using Web Audio API as fallback)
    playNotificationSound();

    // Show browser notification if permission granted
    if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
      new Notification('Pomodoro Timer Complete!', {
        body: mode === 'work' ? 'Time for a break!' : 'Ready to focus?',
        icon: '/favicon.ico'
      });
    }

    if (mode === 'work') {
      const newCount = sessionsCompleted + 1;
      setSessionsCompleted(newCount);
      // Auto-switch to break after 4 pomodoros
      if (newCount % 4 === 0) {
        setMode('longBreak');
        setTimeLeft(TIMER_CONFIG.longBreak);
      } else {
        setMode('shortBreak');
        setTimeLeft(TIMER_CONFIG.shortBreak);
      }
    } else {
      setMode('work');
      setTimeLeft(TIMER_CONFIG.work);
    }
  };

  const playNotificationSound = () => {
    // Use Web Audio API for a simple beep sound as fallback
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
      console.warn('Audio not available:', e);
    }
  };

  const toggleTimer = () => {
    if (!isActive && typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
    setIsActive(!isActive);
  };

  const resetTimer = () => {
    setIsActive(false);
    setTimeLeft(TIMER_CONFIG[mode]);
  };

  const skipPhase = () => {
    if (mode === 'work') {
      setMode('shortBreak');
      setTimeLeft(TIMER_CONFIG.shortBreak);
    } else {
      setMode('work');
      setTimeLeft(TIMER_CONFIG.work);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const progress = ((TIMER_CONFIG[mode] - timeLeft) / TIMER_CONFIG[mode]) * 100;

  const modeConfig = {
    work: { label: 'Focus Time', color: 'bg-red-500', bg: 'bg-red-500/10' },
    shortBreak: { label: 'Short Break', color: 'bg-green-500', bg: 'bg-green-500/10' },
    longBreak: { label: 'Long Break', color: 'bg-blue-500', bg: 'bg-blue-500/10' }
  };

  const config = modeConfig[mode];

  return (
    <Card className={`w-full max-w-md ${config.bg}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          {config.label}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Timer Display */}
        <div className="text-center">
          <div className="text-6xl font-bold font-mono">
            {formatTime(timeLeft)}
          </div>
          <Progress value={progress} className="mt-4 h-2" />
        </div>

        {/* Session Counter */}
        <div className="text-center text-sm text-muted-foreground">
          {sessionsCompleted} pomodoro{sessionsCompleted !== 1 ? 's' : ''} completed today
        </div>

        {/* Controls */}
        <div className="flex justify-center gap-2">
          <Button
            size="lg"
            onClick={toggleTimer}
            className={isActive ? config.color : ''}
          >
            {isActive ? (
              <>
                <Pause className="h-5 w-5 mr-2" />
                Pause
              </>
            ) : (
              <>
                <Play className="h-5 w-5 mr-2" />
                Start
              </>
            )}
          </Button>
          <Button size="lg" variant="outline" onClick={resetTimer}>
            <RotateCcw className="h-5 w-5" />
          </Button>
          <Button size="lg" variant="outline" onClick={skipPhase}>
            <SkipForward className="h-5 w-5" />
          </Button>
        </div>

        {/* Mode Selector */}
        <div className="flex gap-2 justify-center">
          <Button
            size="sm"
            variant={mode === 'work' ? 'default' : 'outline'}
            onClick={() => { setMode('work'); setTimeLeft(TIMER_CONFIG.work); setIsActive(false); }}
          >
            Focus
          </Button>
          <Button
            size="sm"
            variant={mode === 'shortBreak' ? 'default' : 'outline'}
            onClick={() => { setMode('shortBreak'); setTimeLeft(TIMER_CONFIG.shortBreak); setIsActive(false); }}
          >
            Short Break
          </Button>
          <Button
            size="sm"
            variant={mode === 'longBreak' ? 'default' : 'outline'}
            onClick={() => { setMode('longBreak'); setTimeLeft(TIMER_CONFIG.longBreak); setIsActive(false); }}
          >
            Long Break
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
