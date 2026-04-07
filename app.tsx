import React, { useEffect, useState } from 'react';
import { User, fetchUsers, createUser, updateUser, deleteUser } from './api';

const App: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [editId, setEditId] = useState<number | null>(null);
  const [editPassword, setEditPassword] = useState('');

  const loadUsers = async () => {
    try {
      const data = await fetchUsers();
      setUsers(data);
    } catch (e) {
      alert('Error loading users');
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreate = async () => {
    if (!username || !password) {
      alert('Username and password required');
      return;
    }
    try {
      await createUser(username, password);
      setUsername('');
      setPassword('');
      loadUsers();
    } catch (e) {
      alert('Error creating user');
    }
  };

  const handleUpdate = async () => {
    if (editId === null || !editPassword) {
      alert('Password required for update');
      return;
    }
    try {
      await updateUser(editId, editPassword);
      setEditId(null);
      setEditPassword('');
      loadUsers();
    } catch (e) {
      alert('Error updating user');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this user?')) return;
    try {
      await deleteUser(id);
      loadUsers();
    } catch (e) {
      alert('Error deleting user');
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: 'auto', padding: 10 }}>
      <h1>Users CRUD</h1>

      {/* Create user form */}
      <div style={{ marginBottom: 20 }}>
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          style={{ marginRight: 10 }}
        />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={{ marginRight: 10 }}
        />
        <button onClick={handleCreate}>Create</button>
      </div>

      {/* Update password section */}
      {editId !== null && (
        <div style={{ marginBottom: 20 }}>
          <input
            placeholder="New Password"
            type="password"
            value={editPassword}
            onChange={e => setEditPassword(e.target.value)}
            style={{ marginRight: 10 }}
          />
          <button onClick={handleUpdate} style={{ marginRight: 10 }}>
            Update Password
          </button>
          <button onClick={() => setEditId(null)}>Cancel</button>
        </div>
      )}

      {/* Users list */}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #ddd' }}>
            <th style={{ textAlign: 'left', padding: 8 }}>ID</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Username</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{user.id}</td>
              <td style={{ padding: 8 }}>{user.username}</td>
              <td style={{ padding: 8 }}>
                <button onClick={() => {
                  setEditId(user.id);
                  setEditPassword('');
                }} style={{ marginRight: 10 }}>
                  Edit Password
                </button>
                <button onClick={() => handleDelete(user.id)}>Delete</button>
              </td>
            </tr>
          ))}
          {users.length === 0 && (
            <tr>
              <td colSpan={3} style={{ textAlign: 'center', padding: 20 }}>No users found</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default App;
