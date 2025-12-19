import LoginForm from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-screen p-4 gradient-bg-light relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute top-0 left-0 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>

      <div className="relative z-10 w-full animate-scale-in">
        <div className="text-center mb-8 animate-slide-down">
          <h1 className="text-4xl md:text-5xl font-bold text-gradient mb-3">Welcome Back</h1>
          <p className="text-muted-foreground text-lg">Sign in to manage your tasks</p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
