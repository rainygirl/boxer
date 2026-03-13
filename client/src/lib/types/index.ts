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
  key: string;
  disabled_statuses: TaskStatus[];
  owner: User;
  is_favorite: boolean;
  members: ProjectMember[];
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
  number: number;
  ref: string;
  sort_order: number;
  created_by: User;
  created_at: string;
  updated_at: string;
  due_date: string | null;
  subtasks: SubTask[];
}

export interface SubTask {
  id: string;
  parent_task_id: string;
  title: string;
  status: TaskStatus;
  assignee: User | null;
  sub_number: number;
  ref: string;
}

export interface DependencyTask {
  id: string;
  ref: string;
  title: string;
  status: TaskStatus;
  priority: TaskPriority;
  project_id: string;
}

export interface TaskDependencies {
  blocking: DependencyTask[];  // 이 이슈가 기다리는 이슈들
  blocked: DependencyTask[];   // 이 이슈를 기다리는 이슈들
}

export interface TaskActivity {
  id: string;
  activity_type: 'created' | 'status_changed' | 'priority_changed' | 'assignee_changed' | 'content_edited' | 'due_date_changed' | 'project_moved';
  data: Record<string, any>;
  user: User | null;
  created_at: string;
}

export interface TaskComment {
  id: string;
  task_id: string;
  user: User | null;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  type: 'mention' | 'assigned';
  read: boolean;
  created_at: string;
  actor: User | null;
  task_id: string | null;
  task_ref: string | null;
  task_title: string | null;
  project_id: string | null;
}

export interface TaskSearchResult {
  id: string;
  project_id: string;
  project_color: string;
  ref: string;
  title: string;
  status: TaskStatus;
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
