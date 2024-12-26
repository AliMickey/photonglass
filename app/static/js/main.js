const app = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            selectedDevice: '',
            selectedCommand: '',
            targetIp: '',
            selectedIpVersion: 'IPv4',
            isLoading: false,
            commandResult: '',
            devices: window.initialData?.devices ?? [],
            commands: window.initialData?.commands ?? [],
            currentCommand: null,
            showHelp: false,
            showTerms: false,
            isOpen: false,
            isDark: this.getInitialTheme(),
        }
    },

    mounted() {
        this.updateThemeClass();
    },

    watch: {
        selectedCommand: {
            handler(newVal) {
                this.currentCommand = this.commands.find(cmd => cmd.id === newVal);
            },
            immediate: true
        }
    },

    computed: {
        showIpVersionSelector() {
            if (!this.targetIp) return true;

            const ipValidation = {
                v4: /^(\d{1,3}\.){3}\d{1,3}$/,
                v6: /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){0,7}:([0-9a-fA-F]{1,4}:){0,7}[0-9a-fA-F]{1,4}$|^::1$|^::$|^::ffff:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/
            };

            if (ipValidation.v6.test(this.targetIp)) {
                this.selectedIpVersion = 'IPv6';
                return false;
            }
            
            if (ipValidation.v4.test(this.targetIp)) {
                this.selectedIpVersion = 'IPv4';
                return false;
            }

            return true;
        },

        isValidInput() {
            if (!this.currentCommand || !this.targetIp) return false;
            if (this.showIpVersionSelector) return true;
            
            const { validation } = this.currentCommand.field ?? {};
            return validation ? new RegExp(validation).test(this.targetIp) : true;
        }
    },

    methods: {
        getInitialTheme() {
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

        toggleDevice(device) {
            const wasDeselected = this.selectedDevice === device;
            this.selectedDevice = wasDeselected ? '' : device;

            if (wasDeselected) {
                this.resetCommandState();
            }

            this.$nextTick(() => this.$forceUpdate());
        },

        resetCommandState() {
            this.selectedCommand = '';
            this.targetIp = '';
            this.commandResult = '';
        },

        async executeCommand() {
            if (!this.isValidInput) {
                this.commandResult = '❌ Error: Please enter a valid input.';
                return;
            }
        
            this.isLoading = true;
            this.commandResult = '';
        
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        device: this.selectedDevice,
                        command: this.selectedCommand,
                        target: this.targetIp,
                        ipVersion: this.selectedIpVersion
                    })
                });
        
                const data = await response.json();
        
                if (!response.ok || data.error) {
                    this.commandResult = `Error: ${data.message || 'An error occurred.'}`;
                    return;
                }
        
                this.commandResult = data.message || 'Error: No output received from command.';
            } catch (error) {
                this.commandResult = 'Error: An error occurred.';
            } finally {
                this.isLoading = false;
            }
        },
        
        toggleDropdown(event) {
            this.isOpen = !this.isOpen;
        },

        closeDropdown(event) {
            if (!event.target.closest('.relative')) {
                this.isOpen = false;
            }
        },

        selectCommand(command) {
            this.selectedCommand = command;
            setTimeout(() => this.isOpen = false, 100);
        }
    }
});

app.mount('#app');