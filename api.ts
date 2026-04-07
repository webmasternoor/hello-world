export interface User {
  id: number;
  username: string;
}

const API_URL = 'http://127.0.0.1:5000/users';

export async function fetchUsers(): Promise<User[]> {
  const res = await fetch(API_URL);
  return res.json();
}

export async function createUser(username: string, password: string): Promise<User> {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Failed to create user');
  return res.json();
}

export async function updateUser(id: number, password: string): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
  if (!res.ok) throw new Error('Failed to update user');
}

export async function deleteUser(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete user');
}
