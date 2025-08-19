// =============================================================================
// КЛАСС ДЛЯ ФИЛЬТРАЦИИ БИЛЕТОВ
// =============================================================================

class TicketFilter {
    constructor() {
        this.currentStatusFilter = 'all';
        this.currentDrawFilter = 'all';
        this.init();
    }

    init() {
        // Инициализация обработчиков событий для фильтров
        this.bindEvents();
        this.restoreFilters();
        this.applyFilters();
    }

    bindEvents() {
        // Обработчики для фильтров статуса
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentStatusFilter = e.target.getAttribute('data-status');
                this.applyFilters();
                this.saveFilters();
            });
        });

        // Обработчики для фильтров розыгрышей
        document.querySelectorAll('.draw-filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.draw-filter-btn').forEach(b => b.classList.remove('active'));
                e.target.closest('.draw-filter-btn').classList.add('active');
                this.currentDrawFilter = e.target.closest('.draw-filter-btn').getAttribute('data-draw');
                this.applyFilters();
                this.saveFilters();
            });
        });
    }

    filterByStatus(status) {
        // Фильтрация по статусу билетов
        this.currentStatusFilter = status;
        
        // Обновляем активную кнопку
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-status') === status);
        });
        
        this.applyFilters();
        this.saveFilters();
    }

    filterByDraw(drawId) {
        // Фильтрация по розыгрышу
        this.currentDrawFilter = drawId;
        
        // Обновляем активную кнопку
        document.querySelectorAll('.draw-filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-draw') === drawId);
        });
        
        this.applyFilters();
        this.saveFilters();
    }

    applyFilters() {
        // Применение всех активных фильтров
        let visibleTicketsCount = 0;
        let visibleGroupsCount = 0;
        
        document.querySelectorAll('.ticket-group').forEach(group => {
            const groupDrawId = group.getAttribute('data-draw-id');
            let groupVisible = false;
            
            // Фильтр по розыгрышу
            if (this.currentDrawFilter !== 'all' && groupDrawId !== this.currentDrawFilter) {
                group.classList.add('hidden');
                return;
            }

            // Фильтр по статусу билетов внутри группы
            const tickets = group.querySelectorAll('.ticket-item');
            let visibleTicketsInGroup = 0;
            
            tickets.forEach(ticket => {
                const ticketStatus = ticket.getAttribute('data-status');
                const statusMatch = this.currentStatusFilter === 'all' || ticketStatus === this.currentStatusFilter;
                
                if (statusMatch) {
                    ticket.classList.remove('hidden');
                    groupVisible = true;
                    visibleTicketsCount++;
                    visibleTicketsInGroup++;
                } else {
                    ticket.classList.add('hidden');
                }
            });

            // Показываем/скрываем группу
            if (groupVisible) {
                group.classList.remove('hidden');
                visibleGroupsCount++;
                
                // Обновляем счетчик билетов в группе
                const counter = group.querySelector('.tickets-count');
                if (counter) {
                    counter.textContent = `${visibleTicketsInGroup} билетов`;
                }
            } else {
                group.classList.add('hidden');
            }
        });

        this.updateCounter(visibleTicketsCount);
        this.toggleEmptyState(visibleTicketsCount === 0);
    }

    updateCounter(count) {
        // Обновление счетчика видимых билетов
        const counterElement = document.getElementById('visible-tickets-count');
        if (counterElement) {
            counterElement.textContent = count;
        }
    }

    toggleEmptyState(show) {
        // Показать/скрыть состояние "билетов не найдено"
        const emptyState = document.getElementById('empty-state');
        const ticketsContainer = document.getElementById('tickets-container');
        
        if (emptyState && ticketsContainer) {
            if (show) {
                emptyState.classList.add('show');
                ticketsContainer.style.display = 'none';
            } else {
                emptyState.classList.remove('show');
                ticketsContainer.style.display = 'flex';
            }
        }
    }

    saveFilters() {
        // Сохранение состояния фильтров в localStorage
        try {
            const filters = {
                status: this.currentStatusFilter,
                draw: this.currentDrawFilter,
                timestamp: Date.now()
            };
            localStorage.setItem('ticketFilters', JSON.stringify(filters));
        } catch (e) {
            console.warn('Не удалось сохранить фильтры:', e);
        }
    }

    restoreFilters() {
        // Восстановление состояния фильтров из localStorage
        try {
            const savedFilters = localStorage.getItem('ticketFilters');
            if (savedFilters) {
                const filters = JSON.parse(savedFilters);
                
                // Проверяем, что фильтры не слишком старые (1 час)
                if (Date.now() - filters.timestamp < 3600000) {
                    this.currentStatusFilter = filters.status || 'all';
                    this.currentDrawFilter = filters.draw || 'all';
                    
                    // Восстанавливаем активные кнопки
                    document.querySelectorAll('.filter-btn').forEach(btn => {
                        btn.classList.toggle('active', btn.getAttribute('data-status') === this.currentStatusFilter);
                    });
                    
                    document.querySelectorAll('.draw-filter-btn').forEach(btn => {
                        btn.classList.toggle('active', btn.getAttribute('data-draw') === this.currentDrawFilter);
                    });
                }
            }
        } catch (e) {
            console.warn('Не удалось восстановить фильтры:', e);
        }
    }

    clearFilters() {
        // Сброс всех фильтров
        this.currentStatusFilter = 'all';
        this.currentDrawFilter = 'all';
        
        // Сбрасываем активные кнопки
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-status') === 'all');
        });
        
        document.querySelectorAll('.draw-filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-draw') === 'all');
        });
        
        this.applyFilters();
        this.saveFilters();
    }

    // API методы для работы с сервером
    async loadFilteredTickets() {
        try {
            const params = new URLSearchParams({
                status: this.currentStatusFilter,
                draw_id: this.currentDrawFilter
            });
            
            const response = await fetch(`/api/tickets?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderTickets(data.tickets);
                this.updateCounter(data.count);
                this.toggleEmptyState(data.count === 0);
            } else {
                console.error('Ошибка загрузки билетов:', data.error);
                this.showError('Не удалось загрузить билеты');
            }
        } catch (error) {
            console.error('Ошибка запроса:', error);
            this.showError('Ошибка соединения с сервером');
        }
    }

    renderTickets(tickets) {
        // Отрисовка билетов (если нужна динамическая загрузка)
        const container = document.getElementById('tickets-container');
        if (!container) return;
        
        // Реализация отрисовки билетов
        // (можно использовать для AJAX обновления)
    }

    showError(message) {
        // Показ ошибки пользователю
        console.error(message);
        // Можно добавить toast уведомления или другой UI для ошибок
    }
}

// =============================================================================
// ФУНКЦИИ ДЛЯ НАВИГАЦИИ И ВЗАИМОДЕЙСТВИЯ
// =============================================================================

function goToDrawWithTicket(drawId, ticketId) {
    // Переход на страницу розыгрыша с открытой вкладкой "Мои билеты"
    try {
        const url = `/draw/${drawId}?tab=tickets&ticket=${ticketId}`;
        window.location.href = url;
    } catch (error) {
        console.error('Ошибка навигации:', error);
        // Fallback - простой переход на страницу розыгрыша
        window.location.href = `/draw/${drawId}`;
    }
}

function highlightTicket(ticketId) {
    // Подсветка конкретного билета (для deep linking)
    const ticket = document.querySelector(`[data-ticket-id="${ticketId}"]`);
    if (ticket) {
        ticket.scrollIntoView({ behavior: 'smooth', block: 'center' });
        ticket.classList.add('highlighted');
        
        // Убираем подсветку через 3 секунды
        setTimeout(() => {
            ticket.classList.remove('highlighted');
        }, 3000);
    }
}

function shareTicket(ticketId, drawId) {
    // Поделиться билетом (если нужна такая функция)
    const url = `${window.location.origin}/draw/${drawId}?ticket=${ticketId}`;
    
    if (navigator.share) {
        navigator.share({
            title: `Билет #${ticketId}`,
            text: `Мой билет на розыгрыш`,
            url: url
        });
    } else {
        // Fallback - копирование в буфер обмена
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Ссылка скопирована в буфер обмена');
        }).catch(() => {
            console.log('Не удалось скопировать ссылку');
        });
    }
}

function showNotification(message, type = 'info') {
    // Показ уведомлений пользователю
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Автоматическое скрытие через 3 секунды
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// =============================================================================
// ИНИЦИАЛИЗАЦИЯ
// =============================================================================

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, что мы на странице билетов
    if (document.querySelector('.filter-container')) {
        const ticketFilter = new TicketFilter();
        
        // Делаем экземпляр доступным глобально для отладки
        window.ticketFilter = ticketFilter;
        
        // Обработка deep linking (highlight конкретного билета)
        const urlParams = new URLSearchParams(window.location.search);
        const highlightTicketId = urlParams.get('ticket');
        if (highlightTicketId) {
            setTimeout(() => highlightTicket(highlightTicketId), 500);
        }
    }
});

// Обработка изменения размера экрана
window.addEventListener('resize', () => {
    // Можно добавить логику для адаптивности фильтров
});

// Экспорт для использования в других модулях (если нужно)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TicketFilter, goToDrawWithTicket, highlightTicket };
}