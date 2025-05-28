const { createApp, ref, computed, onMounted } = Vue

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

createApp({
  delimiters: ['${', '}'],
  setup() {
    const products = ref([])
    const cart = ref([])
    const errorMessage = ref('')
    const searchQuery = ref('')
    const amountPaid = ref(0)

    onMounted(() => {
      try {
        const raw = document.getElementById('products-data').textContent
        products.value = JSON.parse(raw)
      } catch (e) {
        console.error("JSON xatolik:", e.message)
        errorMessage.value = "Mahsulot ma'lumotlarini yuklab bo‘lmadi"
      }
    })

    const cartItemCount = computed(() => {
      return cart.value.reduce((total, item) => total + item.quantity, 0)
    })

    const cartTotal = computed(() => {
      return cart.value.reduce((total, item) => total + (item.price * item.quantity), 0)
    })

    const addToCart = (product) => {
      if (product.total_quantity <= 0) {
        errorMessage.value = `${product.name} mahsuloti qolmagan!`
        setTimeout(() => errorMessage.value = '', 3000)
        return
      }

      const existing = cart.value.find(item => item.id === product.id)

      if (existing) {
        existing.quantity++
      } else {
        cart.value.push({
          id: product.id,
          name: product.name,
          price: product.latest_selling_price,
          quantity: 1
        })
      }

      product.total_quantity--
    }

    const removeFromCart = (product) => {
      const existing = cart.value.find(item => item.id === product.id)
      const original = products.value.find(p => p.id === product.id)

      if (existing && original) {
        if (existing.quantity > 1) {
          existing.quantity--
        } else {
          const index = cart.value.indexOf(existing)
          if (index > -1) {
            cart.value.splice(index, 1)
          }
        }
        original.total_quantity++
      }
    }

    const searchProducts = computed(() => {
      if (!searchQuery.value) return products.value
      return products.value.filter(p =>
        p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    })

    const showConfirmModal = () => {
      const modal = new bootstrap.Modal(document.getElementById('saleConfirmModal'))
      modal.show()
    }

    const confirmCheckout = async () => {

      if (cart.value.length === 0) {
        errorMessage.value = "Savat bo‘sh! Sotishni amalga oshirib bo‘lmaydi."
        setTimeout(() => errorMessage.value = '', 3000)
        return
      }
      

      const paid = Number(amountPaid.value)
      const total = Number(cartTotal.value)

      if (paid < total) {
        const yetishmaydi = total - paid
        errorMessage.value = `Mijoz bergan pul yetarli emas! Yana ${yetishmaydi.toLocaleString('ru-RU')} so'm kerak.`
        setTimeout(() => errorMessage.value = '', 5000)
        return
      }
      console.log("Paid:", paid, "Total:", total)
      try {
        const response = await axios.post('/process-sale/',
          { products: cart.value },
          {
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            }
          }
        )

        const result = await response.data

        if (result.success) {
          const printWindow = window.open('', '', 'width=350,height=600')

          let receiptHtml = `
                            <html>
                              <head>
                                <title>Chek</title>
                                <style>
                                  body {
                                    font-family: monospace;
                                    font-size: 12px;
                                    width: 280px;
                                    margin: 0 auto;
                                    padding: 10px;
                                  }
                                  h2, h3, p {
                                    text-align: center;
                                    margin: 4px 0;
                                  }
                                  table {
                                    width: 100%;
                                    border-collapse: collapse;
                                    margin-top: 10px;
                                  }
                                  td, th {
                                    padding: 3px 0;
                                    border-bottom: 1px dashed #999;
                                    text-align: left;
                                  }
                                  .total {
                                    font-weight: bold;
                                    text-align: right;
                                    margin-top: 10px;
                                  }
                                </style>
                              </head>
                              <body>
                                <h2>🧾 MarketPro</h2>
                                <p>Haridingiz uchun rahmat!</p>
                                <hr/>
                                <table>
                                  <thead>
                                    <tr>
                                      <th>#</th>
                                      <th>Mahsulot</th>
                                      <th>Soni</th>
                                      <th>Jami</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    ${cart.value.map((item, index) => `
                                      <tr>
                                        <td>${index + 1}</td>
                                        <td>${item.name}</td>
                                        <td>${item.quantity}</td>
                                        <td>${(item.price * item.quantity).toLocaleString('ru-RU')}</td>
                                      </tr>
                                    `).join('')}
                                  </tbody>
                                </table>
                                <hr/>
                                <h3>Jami: ${cartTotal.value.toLocaleString('ru-RU')}</h3>
                                <p>🤝 Yana kutamiz!</p>
                                <script>
                                  window.onload = function() {
                                    window.print();
                                    window.onafterprint = function() {
                                      window.close();
                                    };
                                  };
                                </script>
                              </body>
                            </html>
                          `

          printWindow.document.open()
          printWindow.document.write(receiptHtml)
          printWindow.document.close()

          cart.value = []
          const modalEl = document.getElementById('saleConfirmModal')
          const modal = bootstrap.Modal.getInstance(modalEl)
          modal.hide()
          amountPaid.value = 0


        } else {
          errorMessage.value = result.message || "Xatolik yuz berdi"
          setTimeout(() => errorMessage.value = '', 5000)
        }

      } catch (err) {
        console.error("Server xatoligi:", err)
        errorMessage.value = "Serverga murojaat qilishda xatolik: " + err.message
        setTimeout(() => errorMessage.value = '', 5000)
      }
    }

    const changeAmount = computed(() => {
      const paid = Number(amountPaid.value)
      const total = Number(cartTotal.value)
      return paid >= total ? paid - total : 0
    })

    const clearCartModal = () => {
      const modalEl = document.getElementById('saleConfirmModal')
      const modal = bootstrap.Modal.getInstance(modalEl)
      if (modal) modal.hide()
    }

    const clearCart = () => {
      cart.value.forEach(item => {
        const original = products.value.find(p => p.id === item.id)
        if (original) {
          original.total_quantity += item.quantity  // Savatdagi mahsulot omborga qaytariladi
        }
      })
    
      cart.value = []           // Savatni tozalash
      amountPaid.value = 0      // Mijoz bergan pulni tiklash (agar ishlatilayotgan bo‘lsa)
    
      errorMessage.value = "❌ Harid bekor qilindi"
      setTimeout(() => errorMessage.value = '', 3000)
    }

    const appendDigit = (digit) => {
      amountPaid.value = Number(amountPaid.value.toString() + digit.toString())
    }

    const clearAmount = () => {
      amountPaid.value = 0
    }

    const removeDigit = () => {
      amountPaid.value = Number(amountPaid.value.toString().slice(0, -1) || '0')
    }

    return {
      products,
      cart,
      errorMessage,
      cartItemCount,
      cartTotal,
      addToCart,
      removeFromCart,
      searchQuery,
      searchProducts,
      checkout: confirmCheckout,
      clearCart,
      showConfirmModal,
      amountPaid,
      changeAmount,
      appendDigit,
      clearAmount,
      removeDigit,
      clearCartModal,
    }
  }
}).mount('#app')
