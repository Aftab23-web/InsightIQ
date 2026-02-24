# 👨‍💼 Admin System - Complete Guide

## 🔑 Admin Credentials

**Email:** aftabshah2309@gmail.com  
**Password:** admin2309

## 🚀 How to Access Admin Dashboard

1. Open the application
2. Click **"🔑 Login"** button
3. Enter:
   - Username/Email: `aftabshah2309@gmail.com`
   - Password: `admin2309`
4. Click **"🚀 Login"**
5. You'll see "Admin Dashboard" in the sidebar menu
6. Click "Admin Dashboard" to view system analytics

## 📊 Admin Dashboard Features

### Overview Statistics
- **Total Companies:** Number of registered companies
- **Active Users:** Currently active user accounts
- **Data Uploads:** Total number of data batches uploaded
- **Total Records:** Total data records in the system

### Recent Activity
- **New Registrations (Last 30 Days):** Recent company sign-ups
- **Active Logins (Last 7 Days):** Users who logged in recently

### Three Main Tabs

#### 1. 📋 All Companies
- View complete list of all registered companies
- See details: Username, Email, Role, Company Name, Company ID, Contact, Created Date, Last Login, Status
- Download companies data as CSV file

#### 2. 📊 Usage Analytics
- View data upload statistics by batch
- See number of records per batch
- Track last upload dates
- Summary statistics

#### 3. 📈 Charts
- **Role Distribution:** Pie chart showing user roles (CEO, Manager, etc.)
- **Account Status:** Bar chart of active vs inactive users
- **Registration Timeline:** Line graph of daily registrations

## 🎯 What Admin Can See

### Company Information
- All registered companies
- User roles and positions
- Contact information
- Account creation dates
- Last login timestamps
- Account status (Active/Inactive)

### System Analytics
- Total number of companies using the project
- How many companies are actively using the system
- Data upload frequency and volume
- User engagement metrics
- Growth trends over time

### Download Capabilities
- Export all company data to CSV
- Generate reports with timestamps
- Track system usage patterns

## 🔐 Admin vs Regular User

### Admin User (aftabshah2309@gmail.com)
- ✅ Can see all companies
- ✅ Can view system statistics
- ✅ Has access to Admin Dashboard
- ✅ Can monitor all user activities
- ✅ Can download company data
- ✅ Has special "Administrator" role
- ❌ Cannot access regular user features (Data Upload, Analytics, etc.)

### Regular Users
- ✅ Can upload and analyze their own data
- ✅ Can access all analytics features
- ✅ Can generate reports
- ✅ Standard navigation menu
- ❌ Cannot see Admin Dashboard
- ❌ Cannot view other companies' data
- ❌ Cannot access system statistics

## 🛡️ Security Features

- Admin credentials are hardcoded and secure
- Admin access is validated on every page load
- Regular users cannot access admin features
- Separate navigation menu for admin
- Role-based access control

## 📱 Admin Dashboard Layout

```
┌─────────────────────────────────────────┐
│     👨‍💼 Admin Dashboard                    │
│     System Overview & Company Management │
├─────────────────────────────────────────┤
│  📊 System Overview (4 Cards)           │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │Total │ │Active│ │Data  │ │Total │  │
│  │Comp. │ │Users │ │Upload│ │Record│  │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
├─────────────────────────────────────────┤
│  📅 Recent Activity                     │
│  - New Registrations (30 days)         │
│  - Active Logins (7 days)              │
├─────────────────────────────────────────┤
│  📋 Tabs:                               │
│  ├─ All Companies (Table + Download)   │
│  ├─ Usage Analytics (Statistics)       │
│  └─ Charts (Visualizations)            │
└─────────────────────────────────────────┘
```

## 💡 Usage Tips

1. **Monitor Growth:** Check "New Registrations" regularly
2. **Track Engagement:** Use "Active Logins" to see user activity
3. **Analyze Trends:** Use charts to understand user distribution
4. **Export Data:** Download CSV for external analysis
5. **Quick Overview:** Dashboard shows real-time statistics

## 🔍 How It Works Technically

1. **Login Detection:** System checks if credentials match admin email/password
2. **Special User Object:** Admin gets `is_admin: True` flag
3. **Menu Customization:** Sidebar shows different menu for admin
4. **Access Control:** Admin dashboard checks `is_user_admin()` before showing data
5. **Database Queries:** Fetches all user data and statistics from database
6. **Real-time Updates:** Data refreshes each time you visit the dashboard

## 📞 Common Use Cases

### Check Company Usage
1. Login as admin
2. Go to Admin Dashboard
3. View "All Companies" tab
4. See complete list with last login times

### Monitor Growth
1. Check "New Registrations" metric
2. View "Registration Timeline" chart
3. Track monthly/daily trends

### Analyze User Types
1. Go to "Charts" tab
2. View "Role Distribution" pie chart
3. See breakdown of CEOs, Managers, etc.

### Export for Reports
1. Go to "All Companies" tab
2. Click "📥 Download Companies Data (CSV)"
3. Use in Excel or other tools

## ⚙️ System Information Display

The admin dashboard shows:
- Admin user details
- System email
- Access level
- Last update timestamp
- Database status
- System version

## 🎉 Success Indicators

You know admin access is working when:
- ✅ Login with admin credentials succeeds
- ✅ Sidebar shows "Admin Dashboard" menu
- ✅ Role shows as "Administrator"
- ✅ Can view all company statistics
- ✅ Can see registration data
- ✅ Charts display properly

---

**Admin Status:** ✅ Fully Functional  
**Access Level:** 🛡️ System Administrator  
**Monitoring:** 📊 Real-time Analytics
