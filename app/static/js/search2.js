// static/js/app.js
import { createApp, ref, computed, onMounted } from 'vue'

const App = {
  delimiters: ['${', '}'], // Django templatega mos delimiters
  setup() {
    const products = ref([])
    const search = ref('')
    const cart = ref([])
    const errorMessage = ref('')

    onMounted(() => {
      const jsonData = document.getElementById('products-data').textContent
      products.value = JSON.parse(jsonData)
    })

    const filteredProducts = computed(() => {
      return products.value.filter(p =>
        p.name.toLowerCase().includes(search.value.toLowerCase())
      )
    })

    const addToCart = (product) => {
      if (product.total_quantity <= 0) {
        errorMessage.value = `${product.name} mahsuloti qolmagan!`
        setTimeout(() => errorMessage.value = '', 3000)
        return
      }

      const existing = cart.value.find(item => item.id === product.id)
      if (existing) {
        existing.quantity += 1
      } else {
        cart.value.push({
          id: product.id,
          name: product.name,
          quantity: 1,
          price: product.latest_selling_price
        })
      }

      product.total_quantity -= 1
    }

    const removeFromCart = (product) => {
      const index = cart.value.findIndex(item => item.id === product.id)
      if (index !== -1) {
        cart.value[index].quantity -= 1
        product.total_quantity += 1

        if (cart.value[index].quantity <= 0) {
          cart.value.splice(index, 1)
        }
      }
    }

    const cartTotal = computed(() => {
      return cart.value.reduce((total, item) => total + item.quantity * item.price, 0)
    })

    const cartItemCount = computed(() => {
      return cart.value.reduce((total, item) => total + item.quantity, 0)
    })

    return {
      search,
      products,
      filteredProducts,
      addToCart,
      removeFromCart,
      cart,
      cartTotal,
      cartItemCount,
      errorMessage
    }
  }
}

createApp(App).mount('#app')
