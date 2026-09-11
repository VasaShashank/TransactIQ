import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Navbar } from './components/Navbar';
import { AccountSearch } from './components/AccountSearch';
import { AccountDetail } from './components/AccountDetail';
import { CaseManagement } from './components/CaseManagement';
import { AuditLogViewer } from './components/AuditLogViewer';
import { AlertNotifications } from './components/AlertNotifications';

const MainLayout: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('search');
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [initialCaseAccount, setInitialCaseAccount] = useState<string | null>(null);

  if (!user) {
    return <Login />;
  }

  const handleSelectAccount = (accId: string) => {
    setSelectedAccountId(accId);
    setActiveTab('detail');
  };

  const handleCreateCaseForAccount = (accId: string) => {
    setInitialCaseAccount(accId);
    setActiveTab('cases');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main style={{ flex: 1 }}>
        {activeTab === 'search' && (
          <AccountSearch onSelectAccount={handleSelectAccount} />
        )}

        {activeTab === 'detail' && selectedAccountId && (
          <AccountDetail
            accountId={selectedAccountId}
            onBack={() => setActiveTab('search')}
            onSelectAccount={handleSelectAccount}
            onCreateCaseForAccount={handleCreateCaseForAccount}
          />
        )}

        {activeTab === 'cases' && (
          <CaseManagement
            initialAccountId={initialCaseAccount}
            onClearInitialAccount={() => setInitialCaseAccount(null)}
          />
        )}

        {activeTab === 'audit' && user.role === 'admin' && (
          <AuditLogViewer />
        )}
      </main>

      <AlertNotifications />
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}
