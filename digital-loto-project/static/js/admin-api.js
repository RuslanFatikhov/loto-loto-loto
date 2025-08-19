// admin-api.js - Расширенные функции для работы с API

class AdminAPI {
    constructor() {
        this.baseUrl = window.location.origin;
        this.init();
    }

    init() {
        this.setupErrorHandling();
        this.setupLoadingStates();
    }

    async makeRequest(url, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            this.showLoading(true);
            const response = await fetch(`${this.baseUrl}${url}`, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Произошла ошибка');
            }
            
            return data;
        } catch (error) {
            this.showError(error.message);
            throw error;
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        const loader = document.getElementById('global-loader');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : '#4299e1'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 10000;
            max-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;
        notification.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: none; border: none; color: white; font-size: 18px; cursor: pointer; margin-left: 10px;">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    setupErrorHandling() {
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('Произошла неожиданная ошибка');
        });
    }

    setupLoadingStates() {
        // Создаем глобальный индикатор загрузки
        if (!document.getElementById('global-loader')) {
            const loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.style.cssText = `
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.3);
                z-index: 9999;
                backdrop-filter: blur(2px);
            `;
            loader.innerHTML = `
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                ">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border: 4px solid #e2e8f0;
                        border-top: 4px solid #667eea;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 10px;
                    "></div>
                    <div style="text-align: center; color: #4a5568;">Загрузка...</div>
                </div>
            `;
            document.body.appendChild(loader);

            // Добавляем CSS анимацию
            if (!document.getElementById('loader-styles')) {
                const style = document.createElement('style');
                style.id = 'loader-styles';
                style.textContent = `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }

    // Методы для работы с балансом
    async updateBalance(newBalance) {
        const data = await this.makeRequest('/api/update_balance', {
            method: 'POST',
            body: JSON.stringify({ balance: newBalance })
        });
        
        if (data.success) {
            this.showSuccess('Баланс успешно обновлен!');
            return data.new_balance;
        }
        throw new Error(data.error);
    }

    async addBalance(amount) {
        const data = await this.makeRequest('/api/add_balance', {
            method: 'POST',
            body: JSON.stringify({ amount: amount })
        });
        
        if (data.success) {
            this.showSuccess(`Добавлено ${data.added_amount} COINS к балансу!`);
            return data.new_balance;
        }
        throw new Error(data.error);
    }

    // Методы для работы с розыгрышами
    async getDraws() {
        return await this.makeRequest('/api/draws');
    }

    async createDraw(drawData) {
        const data = await this.makeRequest('/api/draws', {
            method: 'POST',
            body: JSON.stringify(drawData)
        });
        
        if (data.success) {
            this.showSuccess('Розыгрыш успешно создан!');
            return data.draw;
        }
        throw new Error(data.error);
    }

    async updateDraw(drawId, drawData) {
        const data = await this.makeRequest(`/api/draws/${drawId}`, {
            method: 'PUT',
            body: JSON.stringify(drawData)
        });
        
        if (data.success) {
            this.showSuccess('Розыгрыш успешно обновлен!');
            return data.draw;
        }
        throw new Error(data.error);
    }

    async deleteDraw(drawId) {
        const data = await this.makeRequest(`/api/draws/${drawId}`, {
            method: 'DELETE'
        });
        
        if (data.success) {
            this.showSuccess('Розыгрыш успешно удален!');
            return true;
        }
        throw new Error(data.error);
    }

    async conductDraw(drawId) {
        const data = await this.makeRequest('/api/conduct_draw', {
            method: 'POST',
            body: JSON.stringify({ draw_id: drawId })
        });
        
        if (data.success) {
            this.showSuccess(`Розыгрыш проведен! Выигрышные числа: ${data.winning_numbers.join(', ')}`);
            return data;
        }
        throw new Error(data.error);
    }

    // Методы для работы с пакетами
    async getPackages() {
        return await this.makeRequest('/api/packages');
    }

    async createPackage(packageData) {
        const data = await this.makeRequest('/api/packages', {
            method: 'POST',
            body: JSON.stringify(packageData)
        });
        
        if (data.success) {
            this.showSuccess('Пакет успешно создан!');
            return data.package;
        }
        throw new Error(data.error);
    }

    async updatePackage(packageId, packageData) {
        const data = await this.makeRequest(`/api/packages/${packageId}`, {
            method: 'PUT',
            body: JSON.stringify(packageData)
        });
        
        if (data.success) {
            this.showSuccess('Пакет успешно обновлен!');
            return data.package;
        }
        throw new Error(data.error);
    }

    async deletePackage(packageId) {
        const data = await this.makeRequest(`/api/packages/${packageId}`, {
            method: 'DELETE'
        });
        
        if (data.success) {
            this.showSuccess('Пакет успешно удален!');
            return true;
        }
        throw new Error(data.error);
    }

    // Методы для работы со статистикой
    async getStats() {
        return await this.makeRequest('/api/stats');
    }

    async getTickets() {
        return await this.makeRequest('/api/tickets');
    }

    async getBalance() {
        return await this.makeRequest('/api/balance');
    }
}

// Расширенный класс AdminPanel с интеграцией API
class EnhancedAdminPanel extends AdminPanel {
    constructor() {
        super();
        this.api = new AdminAPI();
        this.initRealTimeUpdates();
    }

    async loadInitialData() {
        try {
            // Загружаем все данные параллельно
            const [draws, packages, tickets, balance, stats] = await Promise.all([
                this.api.getDraws(),
                this.api.getPackages(),
                this.api.getTickets(),
                this.api.getBalance(),
                this.api.getStats()
            ]);

            this.updateDrawsTable(draws);
            this.updatePackagesTable(packages);
            this.updateTicketsTable(tickets);
            this.updateBalance(balance.coins);
            this.updateStats(stats);

        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
        }
    }

    async handleDrawSubmit(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const drawData = Object.fromEntries(formData.entries());
        
        try {
            const drawId = drawData.id;
            delete drawData.id;

            if (drawId) {
                await this.api.updateDraw(parseInt(drawId), drawData);
            } else {
                await this.api.createDraw(drawData);
            }

            this.closeDrawModal();
            await this.refreshDrawsTable();

        } catch (error) {
            console.error('Ошибка сохранения розыгрыша:', error);
        }
    }

    async handlePackageSubmit(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const packageData = Object.fromEntries(formData.entries());
        
        try {
            const packageId = packageData.id;
            delete packageData.id;

            if (packageId) {
                await this.api.updatePackage(parseInt(packageId), packageData);
            } else {
                await this.api.createPackage(packageData);
            }

            this.closePackageModal();
            await this.refreshPackagesTable();

        } catch (error) {
            console.error('Ошибка сохранения пакета:', error);
        }
    }

    async refreshDrawsTable() {
        try {
            const draws = await this.api.getDraws();
            this.updateDrawsTable(draws);
        } catch (error) {
            console.error('Ошибка обновления таблицы розыгрышей:', error);
        }
    }

    async refreshPackagesTable() {
        try {
            const packages = await this.api.getPackages();
            this.updatePackagesTable(packages);
        } catch (error) {
            console.error('Ошибка обновления таблицы пакетов:', error);
        }
    }

    updateDrawsTable(draws) {
        const tbody = document.getElementById('draws-table-body');
        tbody.innerHTML = '';

        draws.forEach(draw => {
            const row = document.createElement('tr');
            row.setAttribute('data-draw-id', draw.id);
            
            const statusClass = draw.completed ? 'completed' : 'active';
            const statusText = draw.completed ? 'Завершен' : 'Активен';
            const categoryClass = draw.category === 'big' ? 'big' : 'express';
            
            row.innerHTML = `
                <td>${draw.id}</td>
                <td><span class="category-badge ${categoryClass}">${draw.category}</span></td>
                <td>${draw.title}</td>
                <td>${draw.cost} ${draw.currency}</td>
                <td>${draw.time_left}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${draw.tickets_count || 0}</td>
                <td class="actions">
                    <button onclick="editDraw(${draw.id})" class="btn-edit">Редактировать</button>
                    ${!draw.completed ? `<button onclick="conductDraw(${draw.id})" class="btn-conduct">Провести</button>` : ''}
                    <button onclick="deleteDraw(${draw.id})" class="btn-delete">Удалить</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updatePackagesTable(packages) {
        const tbody = document.getElementById('packages-table-body');
        tbody.innerHTML = '';

        packages.forEach(pkg => {
            const row = document.createElement('tr');
            row.setAttribute('data-package-id', pkg.id);
            
            const categoryText = {
                'big': 'Только крупные',
                'express': 'Только экспресс',
                'all': 'Все розыгрыши'
            }[pkg.category] || pkg.category;

            row.innerHTML = `
                <td>${pkg.id}</td>
                <td>${pkg.name}</td>
                <td><span class="category-badge ${pkg.category}">${categoryText}</span></td>
                <td>${pkg.price} ${pkg.currency}</td>
                <td class="actions">
                    <button onclick="editPackage(${pkg.id})" class="btn-edit">Редактировать</button>
                    <button onclick="deletePackage(${pkg.id})" class="btn-delete">Удалить</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updateTicketsTable(tickets) {
        // Обновление таблицы билетов (если нужно)
        const tbody = document.querySelector('#tickets-section tbody');
        if (tbody) {
            tbody.innerHTML = '';
            
            tickets.forEach(ticket => {
                const row = document.createElement('tr');
                const statusClass = ticket.status === 'winner' ? 'completed' : 'active';
                const statusText = {
                    'active': 'Активен',
                    'winner': 'Выигрыш',
                    'loser': 'Проигрыш'
                }[ticket.status] || ticket.status;

                row.innerHTML = `
                    <td>${ticket.id}</td>
                    <td>Розыгрыш #${ticket.draw_id}</td>
                    <td>${ticket.numbers.join(', ')}</td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td>${new Date(ticket.purchase_date).toLocaleDateString('ru-RU')}</td>
                `;
                tbody.appendChild(row);
            });
        }
    }

    updateBalance(balance) {
        const balanceElement = document.getElementById('display-balance');
        if (balanceElement) {
            balanceElement.textContent = `${balance} COINS`;
        }
    }

    updateStats(stats) {
        // Обновление статистики
        const statElements = {
            'total_tickets': document.querySelector('.stat-card:nth-child(1) .stat-number'),
            'winning_tickets': document.querySelector('.stat-card:nth-child(2) .stat-number'),
            'pending_tickets': document.querySelector('.stat-card:nth-child(3) .stat-number')
        };

        Object.entries(statElements).forEach(([key, element]) => {
            if (element && stats[key] !== undefined) {
                element.textContent = stats[key];
            }
        });
    }

    initRealTimeUpdates() {
        // Периодическое обновление данных (каждые 30 секунд)
        setInterval(async () => {
            if (document.visibilityState === 'visible') {
                try {
                    const stats = await this.api.getStats();
                    this.updateStats(stats);
                } catch (error) {
                    console.error('Ошибка обновления статистики:', error);
                }
            }
        }, 30000);
    }
}

// Обновленные глобальные функции с использованием API
async function updateBalance() {
    const newBalance = document.getElementById('new-balance').value;
    if (!newBalance || newBalance < 0) {
        adminPanel.api.showError('Введите корректную сумму');
        return;
    }
    
    try {
        const balance = await adminPanel.api.updateBalance(parseInt(newBalance));
        adminPanel.updateBalance(balance);
        document.getElementById('new-balance').value = '';
    } catch (error) {
        console.error('Ошибка обновления баланса:', error);
    }
}

async function addBalance() {
    const addAmount = document.getElementById('new-balance').value;
    if (!addAmount || addAmount <= 0) {
        adminPanel.api.showError('Введите корректную сумму для добавления');
        return;
    }
    
    try {
        const balance = await adminPanel.api.addBalance(parseInt(addAmount));
        adminPanel.updateBalance(balance);
        document.getElementById('new-balance').value = '';
    } catch (error) {
        console.error('Ошибка добавления к балансу:', error);
    }
}

async function conductDraw(drawId) {
    if (!confirm('Провести розыгрыш? Это действие нельзя отменить.')) {
        return;
    }
    
    try {
        await adminPanel.api.conductDraw(drawId);
        await adminPanel.refreshDrawsTable();
    } catch (error) {
        console.error('Ошибка проведения розыгрыша:', error);
    }
}

async function deleteDraw(drawId) {
    if (!confirm('Вы уверены, что хотите удалить этот розыгрыш?')) {
        return;
    }
    
    try {
        await adminPanel.api.deleteDraw(drawId);
        await adminPanel.refreshDrawsTable();
    } catch (error) {
        console.error('Ошибка удаления розыгрыша:', error);
    }
}

async function deletePackage(packageId) {
    if (!confirm('Вы уверены, что хотите удалить этот пакет?')) {
        return;
    }
    
    try {
        await adminPanel.api.deletePackage(packageId);
        await adminPanel.refreshPackagesTable();
    } catch (error) {
        console.error('Ошибка удаления пакета:', error);
    }
}

// Инициализация расширенной админ-панели
let adminPanel;
document.addEventListener('DOMContentLoaded', () => {
    adminPanel = new EnhancedAdminPanel();
});