const app = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            // Django templatedan products ma'lumotlarini olish
            products: JSON.parse(document.getElementById('products-data').textContent),
            cart: [],
            errorMessage: ''
        }
    },
    computed: {
        cartItemCount() {
            return this.cart.reduce((total, item) => total + item.quantity, 0)
        },
        cartTotal() {
            return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0)
        }
    },
    methods: {
        addToCart(product) {
            if (product.total_quantity <= 0) {
                this.errorMessage = `${product.name} mahsuloti qolmagan!`
                setTimeout(() => {
                    this.errorMessage = ''
                }, 3000)
                return
            }

            const existingItem = this.cart.find(item => item.id === product.id)
            
            if (existingItem) {
                // Savatdagi miqdor + 1 ombordagi miqdordan oshmasligi kerak
                if (existingItem.quantity + 1 > product.total_quantity) {
                    this.errorMessage = `${product.name} mahsuloti yetarli emas!`
                    setTimeout(() => {
                        this.errorMessage = ''
                    }, 3000)
                    return
                }
                existingItem.quantity++
            } else {
                this.cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.latest_selling_price,
                    quantity: 1
                })
            }product.total_quantity--
        }, 
        
        removeFromCart(product) {
            const existingItem = this.cart.find(item => item.id === product.id)
            
            if (existingItem) {
                if (existingItem.quantity > 1) {
                    existingItem.quantity--
                } else {
                    const index = this.cart.indexOf(existingItem)
                    this.cart.splice(index, 1)
                }
            }product.total_quantity++
        }
    }
})

app.mount('#app')
