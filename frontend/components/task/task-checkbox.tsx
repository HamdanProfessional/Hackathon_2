"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface TaskCheckboxProps {
  checked: boolean;
  onChange: () => void;
  disabled?: boolean;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const sizes = {
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-6 w-6",
};

export default function TaskCheckbox({
  checked,
  onChange,
  disabled = false,
  className,
  size = "md",
}: TaskCheckboxProps) {
  return (
    <button
      type="button"
      onClick={onChange}
      disabled={disabled}
      className={cn(
        "relative inline-flex shrink-0 cursor-pointer rounded border-2 transition-all duration-200",
        "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background",
        sizes[size],
        checked
          ? "border-primary bg-primary hover:bg-primary/90"
          : "border-zinc-600 bg-background hover:border-zinc-500 hover:bg-zinc-900",
        disabled && "cursor-not-allowed opacity-50",
        className
      )}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{
          opacity: checked ? 1 : 0,
          scale: checked ? 1 : 0.5,
        }}
        transition={{
          duration: 0.15,
          ease: "easeOut",
        }}
        className="absolute inset-0 flex items-center justify-center"
      >
        <svg
          className="h-3/5 w-3/5 text-primary-foreground"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={3}
        >
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{
              pathLength: checked ? 1 : 0,
            }}
            transition={{
              duration: 0.2,
              ease: "easeOut",
              delay: checked ? 0.1 : 0,
            }}
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M5 13l4 4L19 7"
          />
        </svg>
      </motion.div>

      {/* Subtle pulse when checked */}
      {checked && (
        <motion.div
          initial={{ opacity: 0, scale: 1 }}
          animate={{
            opacity: [0, 0.3, 0],
            scale: [1, 1.2, 1.4],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            repeatDelay: 2,
          }}
          className="absolute inset-0 rounded bg-primary"
        />
      )}
    </button>
  );
}