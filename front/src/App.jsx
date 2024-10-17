import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import ModalUser from './assets/ModalUser'
import { format } from 'date-fns'

function App({ authenticatedUser, handleLogout }) {
  const [users, setUsers] = useState([])
  const [filteredUsers, setFilteredUsers] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [currentUser, setCurrentUser] = useState(authenticatedUser.username)
  const [allMessages, setAllMessages] = useState([])
  const [userRole, setUserRole] = useState(authenticatedUser.role)
  const [reportedMessages, setReportedMessages] = useState(new Set())

  useEffect(() => {
    fetchUsers()
    fetchAllMessages()
  }, [])

  useEffect(() => {
    if (currentUser) {
      fetchMessages()
    }
  }, [currentUser])

  useEffect(() => {
    const filtered = users.filter(user => 
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.identity.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.identity.lastName.toLowerCase().includes(searchTerm.toLowerCase())
    )
    setFilteredUsers(filtered)
  }, [users, searchTerm])

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/users')
      const usersData = response.data.map(user => ({
        id: user.id,
        username: user.username,
        score: user.score,
        under_investigation: user.under_investigation,
        under_surveillance: user.under_surveillance,
        identity: {
          firstName: user.first_name,
          lastName: user.last_name,
          email: user.email,
          physicalAddress: user.physical_address,
          socialSecurityNumber: user.social_security_number,
          dateOfBirth: user.date_of_birth,
          gender: user.gender,
          ethnicity: user.ethnicity,
          language: user.language
        }
      }))

      setUsers(usersData)
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const fetchMessages = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/messages?user=${currentUser}`)
      setMessages(response.data)
    } catch (error) {
      console.error('Error fetching messages:', error)
    }
  }

  const fetchAllMessages = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/messages')
      setAllMessages(response.data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)))
    } catch (error) {
      console.error('Error fetching all messages:', error)
    }
  }

  const sendMessage = async () => {
    if (!currentUser || !newMessage) return

    try {
      await axios.post('http://localhost:5000/api/message', {
        username: currentUser,
        message: newMessage
      })
      setNewMessage('')
      fetchAllMessages() // Fetch all messages after sending a new one
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  const handleUserSelect = async (user) => {
    setSelectedUser(user);
    setCurrentUser(user.username);
    setUserRole(user.role);
    
    try {
      const response = await axios.get(`http://localhost:5000/api/messages?user=${user.username}`);
      const fetchedMessages = response.data;
      
      // Update the user object with fetched messages
      const updatedUser = { ...user, messages: fetchedMessages };
      setSelectedUser(updatedUser);
      
      // Update the users array with the new user data
      setUsers(prevUsers => prevUsers.map(u => u.id === user.id ? updatedUser : u));
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return format(date, 'MMM d, yyyy HH:mm:ss');
  };

  const logout = () => {
    handleLogout();
    // Clear any stored tokens or session data here
  };

  const reportMessage = async (messageId) => {
    try {
      await axios.post('http://localhost:5000/api/report', {
        message_id: messageId,
        reporter_username: authenticatedUser.username
      })
      setReportedMessages(prev => new Set(prev).add(messageId))
      fetchAllMessages() // Refresh all messages after reporting
    } catch (error) {
      console.error('Error reporting message:', error)
    }
  }

  const deleteMessage = async (messageId) => {
    try {
      await axios.delete(`http://localhost:5000/api/messages/${messageId}`, {
        headers: {
          'username': authenticatedUser.username
        }
      });
      // Refresh messages after successful deletion
      fetchAllMessages();
    } catch (error) {
      console.error('Error deleting message:', error);
      // Handle error (e.g., show an error message to the user)
    }
  };

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="navbar-content">
          <div className="user-info">
            Welcome, {authenticatedUser.username} | Role: {authenticatedUser.role}
          </div>
          <button onClick={logout}>Logout</button>
        </div>
      </nav>

      <div className="main-content">
        {userRole !== 'user' && (
          <div className="user-list">
            <h2>Users</h2>
            <input
              type="text"
              placeholder="Search by name..."
              value={searchTerm}
              onChange={handleSearch}
            />
            {filteredUsers.map(user => (
              <button key={user.id} onClick={() => handleUserSelect(user)}>
                {user.username}
              </button>
            ))}
          </div>
        )}

        <div className="chat-container">
          <h2>All Messages</h2>
          <div className="messages">
            {allMessages.map((message, index) => (
              <div 
                key={index} 
                className={`message-box ${
                  (message.flagged || reportedMessages.has(message.id)) && 
                  (authenticatedUser.role === 'operator' || authenticatedUser.role === 'administrator') 
                    ? 'reported' 
                    : ''
                }`}
              >
                <div className="message-header">
                  <strong>{message.username}</strong>
                  <span className="timestamp">
                    {formatDate(message.date)}
                    {authenticatedUser.role !== "user" ? ` | Score: ${message.score}` : "" }
                  </span>
                </div>
                <div className="message-content">{message.message}</div>
                <button onClick={() => reportMessage(message.id)} className="report-button">
                  Report
                </button>
                {authenticatedUser.role != 'user' && (
                  <button onClick={() => deleteMessage(message.id)} className="delete-button">
                    Delete
                  </button>
                )}
              </div>
            ))}
          </div>

          {authenticatedUser.role !== 'administrator' && (
            <div className="message-input">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message"
              />
              <button onClick={sendMessage}>Send</button>
            </div>
          )}
        </div>
      </div>

      {userRole !== 'user' && (
        <ModalUser
          selectedUser={selectedUser}
          onClose={() => setSelectedUser(null)}
        />
      )}
    </div>
  )
}

export default App
