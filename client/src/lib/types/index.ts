export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'done' | 'confirmed' | 'cancelled';
export type TaskPriority = 'urgent' | 'high' | 'medium' | 'low' | 'none';

export interface User {
  id: number;
  email: string;
  name: string;
  avatar_url: string | null;
}

export type MemberRole = 'owner' | 'member' | 'viewer';

export interface ProjectMember {
  user: User;
  role: MemberRole;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  color: string;
  owner: User;
  created_at: string;
  updated_at: string;
}

export interface TaskAttachment {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  url: string;
  uploaded_by: User;
  created_at: string;
}

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee: User | null;
  sort_order: number;
  created_by: User;
  created_at: string;
  updated_at: string;
}

export const TASK_STATUSES: { value: TaskStatus; label: string; color: string; bg: string }[] = [
  { value: 'backlog',     label: 'Backlog',      color: 'text-white dark:text-slate-900',  bg: 'bg-slate-400 dark:bg-slate-500' },
  { value: 'todo',        label: 'Todo',         color: 'text-white dark:text-slate-900',  bg: 'bg-blue-500' },
  { value: 'in_progress', label: 'In Progress',  color: 'text-white dark:text-slate-900',  bg: 'bg-amber-400' },
  { value: 'done',        label: 'Done',         color: 'text-white dark:text-slate-900',  bg: 'bg-green-500' },
  { value: 'confirmed',   label: 'Confirmed',    color: 'text-white dark:text-slate-900',  bg: 'bg-purple-500' },
  { value: 'cancelled',   label: 'Cancelled',    color: 'text-white dark:text-slate-900',  bg: 'bg-red-400' },
];

export const PRIORITY_CONFIG: { value: TaskPriority; label: string; color: string; icon: string }[] = [
  { value: 'urgent', label: 'Urgent', color: 'text-red-600',    icon: '🔴' },
  { value: 'high',   label: 'High',   color: 'text-orange-500', icon: '🟠' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-500', icon: '🟡' },
  { value: 'low',    label: 'Low',    color: 'text-blue-400',   icon: '🔵' },
  { value: 'none',   label: 'None',   color: 'text-slate-400',  icon: '⚪' },
];
