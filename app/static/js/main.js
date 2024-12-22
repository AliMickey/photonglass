const app = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            selectedDevice: '',
            selectedCommand: '',
            targetIp: '',
            isLoading: false,
            isLoadingIp: false,
            commandResult: '',
            devices: window.initialData?.devices || [],
            commands: window.initialData?.commands || [],
            currentCommand: null,
            showHelp: false,
            showTerms: false,
            isOpen: false,
            isDark: localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches),
            site_config: window.initialData?.site_config || {},
            peeringdbUrl: window.initialData?.site_config?.footer?.external_links?.peeringdb || '',
            githubUrl: window.initialData?.site_config?.footer?.external_links?.github || ''
        }
    },
    mounted() {
        this.updateThemeClass();
        // Make sure commands are loaded
        if (window.initialData?.commands) {
            console.log('Commands loaded:', this.commands);
        }
    },
    watch: {
        selectedCommand: {
            handler(newVal) {
                this.currentCommand = this.commands.find(cmd => cmd.id === newVal);
                console.log("Current command updated:", this.currentCommand);
            },
            immediate: true
        }
    },
    computed: {
        isValidInput() {
            if (!this.currentCommand || !this.targetIp) return false;
            if (this.currentCommand.field?.validation) {
                const pattern = new RegExp(this.currentCommand.field.validation);
                return pattern.test(this.targetIp);
            }
            return true;
        }
    },
    methods: {
        async getMyIp() {
            if (this.isLoadingIp) return;
            this.isLoadingIp = true;
            try {
                const response = await fetch('/my-ip');
                const data = await response.json();
                if (response.ok && data.ip) {
                    this.targetIp = data.ip;
                } else {
                    console.error('Failed to get IP address');
                }
            } catch (error) {
                console.error('Error fetching IP:', error);
            } finally {
                this.isLoadingIp = false;
            }
        },
        toggleTheme() {
            this.isDark = !this.isDark;
            localStorage.theme = this.isDark ? 'dark' : 'light';
            this.updateThemeClass();
        },
        updateThemeClass() {
            if (this.isDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        },
        toggleDevice(device) {
            // Update the selected device state
            const wasDeselected = this.selectedDevice === device;
            this.selectedDevice = wasDeselected ? '' : device;
            
            // Only reset states if we're deselecting the device entirely
            if (wasDeselected) {
                this.selectedCommand = '';
                this.targetIp = '';
                this.commandResult = '';
            }

            // Force a re-render to ensure styling is updated
            this.$nextTick(() => {
                this.$forceUpdate();
            });
        },
        async executeCommand() {
            if (!this.isValidInput) {
                this.commandResult = '❌ Error: Please enter a valid input according to the command requirements';
                return;
            }

            this.isLoading = true;
            this.commandResult = '';

            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        device: this.selectedDevice,
                        command: this.selectedCommand,
                        target: this.targetIp
                    })
                });

                const data = await response.json();
                
                if (!response.ok) {
                    this.commandResult = `❌ Error: ${data.message || 'An unknown error occurred'}`;
                    return;
                }

                if (data.error) {
                    // Handle error responses with specific error types
                    const errorPrefix = data.error_type === 'timeout' ? '🕒 Timeout Error: ' :
                                      data.error_type === 'auth' ? '🔒 Authentication Error: ' :
                                      data.error_type === 'connection' ? '🔌 Connection Error: ' :
                                      data.error_type === 'no_output' ? '📭 No Output Error: ' :
                                      '❌ Error: ';
                    this.commandResult = errorPrefix + data.message;
                    return;
                }

                // Handle successful response
                if (data.result) {
                    this.commandResult = data.result;
                } else {
                    this.commandResult = '❌ Error: No output received from command';
                }
            } catch (error) {
                console.error('Command execution error:', error);
                this.commandResult = '❌ Error: Failed to execute command. Please try again.';
            } finally {
                this.isLoading = false;
            }
        },
        toggleDropdown(event) {
            this.isOpen = !this.isOpen;
        },
        closeDropdown(event) {
            // Only close if clicking outside the dropdown
            if (!event.target.closest('.relative')) {
                this.isOpen = false;
            }
        },
        selectCommand(command) {
            this.selectedCommand = command;
            // Add a small delay before closing to ensure the selection is visible
            setTimeout(() => {
                this.isOpen = false;
            }, 100);
        }
    }
});

app.mount('#app');