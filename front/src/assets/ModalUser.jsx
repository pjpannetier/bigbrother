import React from 'react';

function ModalUser({ selectedUser, onClose }) {
  if (!selectedUser) return null;

  const getRights = (score) => {
    if (score > 75) {
      return {
        creditInterest: '0%',
        vat: 'No VAT on consumer goods',
        surveillance: false,
        credit: true,
        policeAction: false
      };
    } else if (score > 50) {
      return {
        creditInterest: '1.5%',
        vat: '10%',
        surveillance: false,
        credit: true,
        policeAction: false
      };
    } else if (score >= 25) {
      return {
        creditInterest: '5%',
        vat: '30%',
        surveillance: false,
        credit: true,
        policeAction: false
      };
    } else if (score >= 15) {
      return {
        creditInterest: 'N/A',
        vat: '100%',
        surveillance: true,
        credit: false,
        policeAction: false
      };
    } else {
      return {
        creditInterest: 'N/A',
        vat: '100%',
        surveillance: true,
        credit: false,
        policeAction: true
      };
    }
  };

  const userRights = getRights(selectedUser.score);

  return (
    <div className="modal">
      <div className="modal-content">
        <button className="close-button" onClick={onClose}>×</button>
        <h2>{selectedUser.username}</h2>
        <table>
          <tbody>
            <tr>
              <th>ID:</th>
              <td>{selectedUser.id}</td>
            </tr>
            <tr>
              <th>Overall Score:</th>
              <td>{selectedUser.score}</td>
            </tr>
            <tr>
              <th>Under Investigation:</th>
              <td>{selectedUser.under_investigation ? 'Yes' : 'No'}</td>
            </tr>
            <tr>
              <th>Under Surveillance:</th>
              <td>{selectedUser.under_surveillance ? 'Yes' : 'No'}</td>
            </tr>
            <tr>
              <th>Role:</th>
              <td>{selectedUser.role}</td>
            </tr>
          </tbody>
        </table>
        
        <h3>Identity Information:</h3>
        <table>
          <tbody>
            <tr>
              <th>Name:</th>
              <td>{selectedUser.identity.firstName} {selectedUser.identity.lastName}</td>
            </tr>
            <tr>
              <th>Email:</th>
              <td>{selectedUser.identity.email}</td>
            </tr>
            <tr>
              <th>Address:</th>
              <td>{selectedUser.identity.physicalAddress}</td>
            </tr>
            <tr>
              <th>SSN:</th>
              <td>{selectedUser.identity.socialSecurityNumber}</td>
            </tr>
            <tr>
              <th>Date of Birth:</th>
              <td>{new Date(selectedUser.identity.dateOfBirth).toLocaleDateString()}</td>
            </tr>
            <tr>
              <th>Gender:</th>
              <td>{selectedUser.identity.gender}</td>
            </tr>
            <tr>
              <th>Ethnicity:</th>
              <td>{selectedUser.identity.ethnicity}</td>
            </tr>
            <tr>
              <th>Language:</th>
              <td>{selectedUser.identity.language}</td>
            </tr>
          </tbody>
        </table>
        
        <h3>Rights:</h3>
        <table>
          <tbody>
            <tr>
              <th>Credit Interest:</th>
              <td>{userRights.creditInterest}</td>
            </tr>
            <tr>
              <th>VAT:</th>
              <td>{userRights.vat}</td>
            </tr>
            <tr>
              <th>Under Surveillance:</th>
              <td>{userRights.surveillance ? 'Yes' : 'No'}</td>
            </tr>
            <tr>
              <th>Credit Authorized:</th>
              <td>{userRights.credit ? 'Yes' : 'No'}</td>
            </tr>
            <tr>
              <th>Police Action:</th>
              <td>{userRights.policeAction ? 'Police sent to home' : 'No'}</td>
            </tr>
          </tbody>
        </table>
        
        <h3>Recent Messages:</h3>
        <div className="user-messages">
          {selectedUser.messages && selectedUser.messages.map((msg) => (
            <div key={msg.id} className="user-message">
              <p>{msg.message}</p>
              <table>
                <tbody>
                  <tr>
                    <th>Score:</th>
                    <td>{msg.score}</td>
                  </tr>
                  <tr>
                    <th>Date:</th>
                    <td>{new Date(msg.date).toLocaleString()}</td>
                  </tr>
                  <tr>
                    <th>Flagged:</th>
                    <td>{msg.flagged ? 'Yes' : 'No'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ModalUser;
