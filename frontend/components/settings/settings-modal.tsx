"use client";

import { useState, useEffect } from "react";
import { Settings, Download, LayoutGrid, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { apiClient, type UserPreferences } from "@/lib/api";
import { toast } from "sonner";

export function SettingsModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [preferences, setPreferences] = useState<UserPreferences>({});
  const [isLoading, setIsLoading] = useState(false);

  // Load preferences when modal opens
  useEffect(() => {
    if (isOpen) {
      loadPreferences();
    }
  }, [isOpen]);

  const loadPreferences = async () => {
    try {
      const user = await apiClient.getUserPreferences();
      setPreferences(user.preferences || {});
    } catch (error) {
      console.error("Failed to load preferences:", error);
    }
  };

  const updatePreference = async (key: keyof UserPreferences, value: any) => {
    const newPreferences = { ...preferences, [key]: value };
    setPreferences(newPreferences);

    // Sync viewMode to localStorage for cross-tab communication
    if (key === 'viewMode' && typeof window !== 'undefined') {
      localStorage.setItem('viewMode', value);
    }

    try {
      await apiClient.updateUserPreferences(newPreferences);
      toast.success("Preference updated successfully");
    } catch (error) {
      toast.error("Failed to update preference");
      // Revert on error
      setPreferences(preferences);
      if (key === 'viewMode' && typeof window !== 'undefined') {
        localStorage.setItem('viewMode', preferences.viewMode || 'grid');
      }
    }
  };

  const handleExportData = async () => {
    setIsLoading(true);
    try {
      const blob = await apiClient.exportUserData();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      // Use default filename for now
      // Note: If we need to extract filename from headers, we'd need to modify the API method to return headers
      let filename = "todo-export.json";

      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success("Data exported successfully!");
    } catch (error) {
      toast.error("Failed to export data");
      console.error("Export error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon">
          <Settings className="h-4 w-4" />
          <span className="sr-only">Settings</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Customize your experience and manage your data.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Preferences Section */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Preferences</h4>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="show-completed">Show Completed Tasks</Label>
                <p className="text-xs text-muted-foreground">
                  Display completed tasks in the main view
                </p>
              </div>
              <Switch
                id="show-completed"
                checked={preferences.showCompleted || false}
                onCheckedChange={(checked) =>
                  updatePreference("showCompleted", checked)
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="compact-view">Compact View</Label>
                <p className="text-xs text-muted-foreground">
                  Use a more compact layout for tasks
                </p>
              </div>
              <Switch
                id="compact-view"
                checked={preferences.compactView || false}
                onCheckedChange={(checked) =>
                  updatePreference("compactView", checked)
                }
              />
            </div>

            <div className="space-y-2">
              <Label>View Mode</Label>
              <p className="text-xs text-muted-foreground">
                Choose how tasks are displayed
              </p>
              <div className="flex gap-2 p-1 bg-muted rounded-lg">
                <Button
                  type="button"
                  variant={preferences.viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  className="flex-1"
                  onClick={() => updatePreference("viewMode", "grid")}
                >
                  <LayoutGrid className="h-4 w-4 mr-2" />
                  Grid
                </Button>
                <Button
                  type="button"
                  variant={preferences.viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  className="flex-1"
                  onClick={() => updatePreference("viewMode", "list")}
                >
                  <List className="h-4 w-4 mr-2" />
                  List
                </Button>
              </div>
            </div>
          </div>

          <Separator />

          {/* Data Management Section */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Data Management</h4>

            <Button
              onClick={handleExportData}
              disabled={isLoading}
              className="w-full justify-start"
              variant="outline"
            >
              <Download className="mr-2 h-4 w-4" />
              {isLoading ? "Exporting..." : "Export All Data"}
            </Button>

            <p className="text-xs text-muted-foreground">
              Download all your tasks and preferences as a JSON file.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}