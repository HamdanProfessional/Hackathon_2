"use client";

import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useDebounce } from "@/hooks/use-debounce";
import { useEffect, useState } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";

interface SearchBarProps {
  className?: string;
  placeholder?: string;
}

export function SearchBar({ className, placeholder = "Search tasks..." }: SearchBarProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const [searchValue, setSearchValue] = useState(searchParams.get("search") || "");
  const debouncedSearch = useDebounce(searchValue, 300);

  // Update URL when debounced search changes
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());

    if (debouncedSearch) {
      params.set("search", debouncedSearch);
    } else {
      params.delete("search");
    }

    // Update URL without causing a navigation
    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl);
  }, [debouncedSearch, pathname]);

  // Handle direct input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(e.target.value);
  };

  return (
    <div className={cn("relative", className)}>
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
      <Input
        type="text"
        placeholder={placeholder}
        value={searchValue}
        onChange={handleInputChange}
        className="pl-10 bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-500 focus:border-violet-500 focus:ring-violet-500/20"
      />
    </div>
  );
}