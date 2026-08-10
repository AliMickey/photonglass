// Loose patterns for the target field, where the server has the final say
const targetValidation = {
    v4: /^(\d{1,3}\.){3}\d{1,3}$/,
    v6: /^([0-9a-fA-F]{0,4}:){2,7}([0-9a-fA-F]{0,4}|\d{1,3}(\.\d{1,3}){3})$/,
    hostname: /^[\p{L}\p{N}][\p{L}\p{N}-]*(\.[\p{L}\p{N}][\p{L}\p{N}-]*)+$/u,
    mask: /^\d{1,3}$/
};

const app = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            selectedDevices: [],
            selectedCommand: '',
            targetIp: '',
            selectedIpVersion: 'IPv4',
            isLoading: false,
            results: {},
            resultOrder: [],
            devices: window.initialData?.devices ?? {},
            commands: window.initialData?.commands ?? {},
            maxDevices: window.initialData?.maxDevices ?? 0,
            currentCommand: null,
            showHelp: false,
            showTerms: false,
            expandedDevice: null,
            expandedPlaceholder: 0,
            isOpen: false,
            highlightedIndex: -1,
            lastFocused: null,
            isDark: this.getInitialTheme(),
        }
    },

    mounted() {
        this.updateThemeClass();
        document.addEventListener('click', this.handleDocumentClick);
        document.addEventListener('keydown', this.handleKeydown);
    },

    unmounted() {
        document.removeEventListener('click', this.handleDocumentClick);
        document.removeEventListener('keydown', this.handleKeydown);
    },

    watch: {
        showHelp(isOpen) {
            this.syncModalFocus(isOpen);
        },
        showTerms(isOpen) {
            this.syncModalFocus(isOpen);
        },
        expandedDevice(deviceKey) {
            this.syncModalFocus(Boolean(deviceKey));
        },
        selectedDevices: {
            handler(newVal) {
                if (!newVal.length) {
                    this.resetCommandState();
                    return;
                }
                // Drop the command if it is not supported by every selected device
                if (!this.filteredCommands.some(command => command.key === this.selectedCommand)) {
                    this.selectedCommand = '';
                }
            },
            
            immediate: true
        },
        selectedCommand: {
            handler(newVal) {
                this.currentCommand = this.commands[newVal] || null;
            },
            immediate: true
        }
    },

    computed: {
        devicesList() {
            return Object.entries(this.devices).map(([key, device]) => ({
                key,
                ...device
            }));
        },

        filteredCommands() {
            if (!this.selectedDevices.length) return [];

            // Only commands every selected device supports can be run together
            const shared = this.selectedDevices
                .map(deviceKey => this.devices[deviceKey]?.commands ?? [])
                .reduce((acc, commands) => acc.filter(commandKey => commands.includes(commandKey)));

            return shared.map(commandKey => ({
                key: commandKey,
                ...this.commands[commandKey]
            }));
        },

        // No more devices may be added once the configured cap is hit
        isDeviceLimitReached() {
            return this.maxDevices > 0 && this.selectedDevices.length >= this.maxDevices;
        },

        resultPanels() {
            return this.resultOrder.map(deviceKey => ({
                key: deviceKey,
                device: this.devices[deviceKey] ?? {},
                ...this.results[deviceKey]
            }));
        },

        // Commands some, but not all, of the selected devices support
        unavailableCommands() {
            if (!this.selectedDevices.length) return [];

            const shared = new Set(this.filteredCommands.map(command => command.key));

            return Object.keys(this.commands)
                .filter(commandKey => !shared.has(commandKey))
                .map(commandKey => ({
                    key: commandKey,
                    ...this.commands[commandKey],
                    missing: this.selectedDevices
                        .filter(deviceKey => !(this.devices[deviceKey]?.commands ?? []).includes(commandKey))
                        .map(deviceKey => this.devices[deviceKey]?.display_name || deviceKey)
                }))
                .filter(command => command.missing.length < this.selectedDevices.length);
        },

        resultStatus() {
            if (!this.resultOrder.length) return '';

            const total = this.resultOrder.length;
            const label = total === 1 ? 'device' : 'devices';
            const finished = this.resultOrder.filter(deviceKey => this.results[deviceKey]?.done).length;

            return finished < total
                ? `Running on ${total} ${label}, ${finished} finished`
                : `Finished on ${total} ${label}`;
        },

        showIpVersionSelector() {
            if (!this.targetIp) return true;

            // A prefix still names an address family, so match on the address on its own
            const address = this.targetIp.split('/')[0];

            if (targetValidation.v6.test(address)) {
                this.selectedIpVersion = 'IPv6';
                return false;
            }

            if (targetValidation.v4.test(address)) {
                this.selectedIpVersion = 'IPv4';
                return false;
            }

            return true;
        },

        isValidInput() {
            if (!this.currentCommand || !this.targetIp) return false;

            const { type } = this.currentCommand.field ?? {};

            const [address, mask, extra] = this.targetIp.split('/');
            const isAddress = extra === undefined && (targetValidation.v4.test(address) || targetValidation.v6.test(address));

            if (type === 'address') return isAddress && mask === undefined;
            if (type === 'prefix') return isAddress && (mask === undefined || targetValidation.mask.test(mask));
            if (type === 'hostname') return !isAddress && targetValidation.hostname.test(this.targetIp);

            return true;
        }
    },

    methods: {
        getInitialTheme() {
            const forcedTheme = window.initialData?.forcedTheme;
            if (forcedTheme) return forcedTheme === 'dark';

            return localStorage.theme === 'dark' || 
                   (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
        },

        toggleIpVersion() {
            this.selectedIpVersion = this.selectedIpVersion === 'IPv4' ? 'IPv6' : 'IPv4';
        },

        toggleTheme() {
            this.isDark = !this.isDark;
            localStorage.theme = this.isDark ? 'dark' : 'light';
            this.updateThemeClass();
        },

        updateThemeClass() {
            document.documentElement.classList[this.isDark ? 'add' : 'remove']('dark');
        },

        isDeviceDisabled(deviceKey) {
            return this.isLoading || (this.isDeviceLimitReached && !this.selectedDevices.includes(deviceKey));
        },

        toggleDevice(deviceKey) {
            if (this.isDeviceDisabled(deviceKey)) return;

            if (this.selectedDevices.includes(deviceKey)) {
                this.selectedDevices = this.selectedDevices.filter(key => key !== deviceKey);
                return;
            }
            // Rebuilt from the device list so the selection keeps the configured order
            this.selectedDevices = Object.keys(this.devices)
                .filter(key => key === deviceKey || this.selectedDevices.includes(key));
        },

        resetCommandState() {
            this.selectedCommand = '';
            this.targetIp = '';
            this.results = {};
            this.resultOrder = [];
            this.expandedDevice = null;
        },

        finishPendingResults(message) {
            for (const deviceKey of this.resultOrder) {
                const result = this.results[deviceKey];
                if (result.done) continue;

                result.done = true;
                result.error = message;
            }
        },

        toggleResult(deviceKey) {
            const result = this.results[deviceKey];
            if (result) result.collapsed = !result.collapsed;
        },

        toggleExpand(deviceKey) {
            const card = [...(this.$refs.results?.querySelectorAll('[data-panel]') ?? [])].find(el => el.dataset.panel === deviceKey);
            const from = card?.getBoundingClientRect();

            if (this.expandedDevice === deviceKey) {
                this.expandedDevice = null;
            } else {
                const result = this.results[deviceKey];
                if (result) result.collapsed = false;
                // Holds the grid slot open so the other cards do not reflow
                if (from) this.expandedPlaceholder = from.height;
                this.expandedDevice = deviceKey;
            }

            if (from) this.$nextTick(() => this.morphCard(card, from));
        },

        // The card snaps straight to its new box, so replay the old box as a transform
        morphCard(card, from) {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

            const to = card.getBoundingClientRect();
            if (!to.width || !to.height) return;

            card.getAnimations().forEach(animation => animation.cancel());

            card.animate([
                {
                    transformOrigin: 'top left',
                    transform: `translate(${from.left - to.left}px, ${from.top - to.top}px) scale(${from.width / to.width}, ${from.height / to.height})`
                },
                { transformOrigin: 'top left', transform: 'none' }
            ], { duration: 240, easing: 'cubic-bezier(0.2, 0, 0, 1)' });
        },

        async copyResult(deviceKey) {
            const result = this.results[deviceKey];
            if (!result) return;

            const text = result.error || result.output;
            if (!text) return;

            try {
                await navigator.clipboard.writeText(text);
            } catch (error) {
                // navigator.clipboard is unavailable outside secure contexts
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                textarea.remove();
            }

            result.copied = true;
            setTimeout(() => { result.copied = false; }, 1500);
        },

        async executeCommand() {
            if (!this.isValidInput) {
                return;
            }
        
            this.isLoading = true;
            this.resultOrder = [...this.selectedDevices];
            this.expandedDevice = null;
            this.results = Object.fromEntries(
                this.resultOrder.map((deviceKey, index) => [deviceKey, { output: '', error: '', done: false, collapsed: index > 0, copied: false }])
            );

            this.$nextTick(() => this.$refs.results?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
        
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        devices: this.selectedDevices,
                        command: this.selectedCommand,
                        target: this.targetIp,
                        ipVersion: this.selectedIpVersion
                    })
                });
        
                if (!response.ok || !response.body) {
                    // Rejected input comes back with a message worth showing; anything else stays generic
                    const rejection = await response.json().catch(() => null);
                    this.finishPendingResults(`Error: ${rejection?.message || 'An error occurred.'}`);
                    return;
                }

                await this.readStream(response);
                this.finishPendingResults('Error: An error occurred.');
            } catch (error) {
                this.finishPendingResults('Error: An error occurred.');
            } finally {
                this.isLoading = false;
            }
        },

        async readStream(response) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let pending = this.resultOrder.length;

            while (pending > 0) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Each complete line is one JSON chunk; the last piece may be partial
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line) continue;

                    const chunk = JSON.parse(line);
                    const result = this.results[chunk.device];

                    if (!result || result.done) continue;

                    if (chunk.error) {
                        result.error = 'Error: An error occurred.';
                        result.done = true;
                        pending--;
                    } else if (chunk.done) {
                        result.done = true;
                        pending--;
                    } else {
                        result.output += chunk.message;
                    }
                }
            }

            // The response is left to drain on its own so the server can finish logging
        },
        
        toggleDropdown() {
            this.isOpen = !this.isOpen;
            if (this.isOpen) this.syncHighlight();
        },

        syncHighlight() {
            const index = this.filteredCommands.findIndex(command => command.key === this.selectedCommand);
            this.highlightedIndex = index === -1 ? 0 : index;
        },

        moveHighlight(step) {
            if (!this.isOpen) {
                this.isOpen = true;
                this.syncHighlight();
                return;
            }

            const count = this.filteredCommands.length;
            if (!count) return;

            this.highlightedIndex = (this.highlightedIndex + step + count) % count;
            this.$nextTick(() => {
                document.getElementById(`command-option-${this.highlightedIndex}`)?.scrollIntoView({ block: 'nearest' });
            });
        },

        chooseHighlighted() {
            if (!this.isOpen) {
                this.isOpen = true;
                this.syncHighlight();
                return;
            }

            const command = this.filteredCommands[this.highlightedIndex];
            if (command) this.selectCommand(command.key);
        },

        selectCommand(command) {
            this.selectedCommand = command;
            this.isOpen = false;
        },

        handleDocumentClick(event) {
            if (!event.target.closest('[data-dropdown]')) {
                this.isOpen = false;
            }
        },

        handleKeydown(event) {
            if (event.key === 'Escape') {
                this.isOpen = false;
                this.showHelp = false;
                this.showTerms = false;
                this.expandedDevice = null;
                return;
            }

            if (event.key === 'Tab' && (this.showHelp || this.showTerms || this.expandedDevice)) {
                this.trapFocus(event);
            }
        },

        trapFocus(event) {
            const modal = document.querySelector('[data-modal]');
            if (!modal) return;

            const focusable = modal.querySelectorAll('a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (!focusable.length) return;

            const first = focusable[0];
            const last = focusable[focusable.length - 1];

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        },

        syncModalFocus(isOpen) {
            // Every modal — help, terms and the expanded result — locks the page behind it
            document.body.classList.toggle('overflow-hidden', isOpen);

            if (isOpen) {
                this.lastFocused = document.activeElement;
                this.$nextTick(() => document.querySelector('[data-modal] button')?.focus());
                return;
            }

            this.lastFocused?.focus();
            this.lastFocused = null;
        }
    }
});

app.mount('#app');